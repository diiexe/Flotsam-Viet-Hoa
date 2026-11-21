"""
Flotsam Vietnamese Localization & Font SDF Patch Builder
Author: Diiexe (https://github.com/diiexe)
"""
import UnityPy, struct, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = SCRIPT_DIR
SRC_DIR = os.path.dirname(TOOLS_DIR)
REPO_DIR = os.path.dirname(SRC_DIR)

def _resolve_game_data_dir():
    for arg in sys.argv[1:]:
        if not arg.startswith("-") and os.path.isdir(arg):
            if os.path.exists(os.path.join(arg, "Flotsam_Data", "resources.assets")):
                return os.path.join(arg, "Flotsam_Data")
            if os.path.exists(os.path.join(arg, "resources.assets")):
                return arg
    for candidate in (
        r"C:\Program Files\Epic Games\Flotsam\Flotsam_Data",
        r"D:\Epic Games\Flotsam\Flotsam_Data",
        r"E:\Epic Games\Flotsam\Flotsam_Data",
        r"C:\Program Files (x86)\Steam\steamapps\common\Flotsam\Flotsam_Data",
        r"D:\SteamLibrary\steamapps\common\Flotsam\Flotsam_Data",
        r"E:\SteamLibrary\steamapps\common\Flotsam\Flotsam_Data",
    ):
        if os.path.exists(os.path.join(candidate, "resources.assets")):
            return candidate
    return r"C:\Program Files\Epic Games\Flotsam\Flotsam_Data"

GAME_DATA_DIR = _resolve_game_data_dir()
BACKUP_DIR = os.path.join(GAME_DATA_DIR, "backup_goc")

def get_clean_resource_path():
    candidates = [
        os.path.join(BACKUP_DIR, "resources.assets"),
        os.path.join(GAME_DATA_DIR, "resources.assets"),
        os.path.join(SCRIPT_DIR, "backup", "resources.assets.bak")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("Could not find clean resources.assets!")

def get_clean_sharedassets0_path():
    candidates = [
        os.path.join(BACKUP_DIR, "sharedassets0.assets"),
        os.path.join(GAME_DATA_DIR, "sharedassets0.assets"),
        os.path.join(SCRIPT_DIR, "backup", "sharedassets0.assets.bak")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("Could not find clean sharedassets0.assets!")

def pad4(b):
    rem = len(b) % 4
    if rem != 0:
        return b + b'\x00' * (4 - rem)
    return b

def _skip_str(data, off):
    n = struct.unpack_from('<I', data, off)[0]
    off += 4 + n
    if n % 4 != 0:
        off += 4 - (n % 4)
    return off

def _read_mb_name(raw):
    if len(raw) < 32:
        return None, 0
    nlen = struct.unpack_from('<I', raw, 28)[0]
    if nlen == 0 or nlen > 256 or 32 + nlen > len(raw):
        return None, 0
    try:
        return raw[32:32 + nlen].decode('utf-8'), _skip_str(raw, 28)
    except UnicodeDecodeError:
        return None, 0

def _parse_i2_offsets(raw, terms_off):
    """Tính động tail_off, số ngôn ngữ và sync_off trong LanguageSourceData, kiểm tra khớp 100% cuối object."""
    off = terms_off
    orig_total_terms = struct.unpack_from('<I', raw, off)[0]
    off += 4
    for _ in range(orig_total_terms):
        off = _skip_str(raw, off)  # term name
        off += 4  # term type
        lc = struct.unpack_from('<I', raw, off)[0]
        off += 4
        for _ in range(lc):
            off = _skip_str(raw, off)
        fl = struct.unpack_from('<I', raw, off)[0]
        off += 4 + fl
        if fl % 4 != 0:
            off += 4 - (fl % 4)
        off += 4  # touch_date

    tail_off = off
    orig_lang_cnt = struct.unpack_from('<I', raw, tail_off + 12)[0]
    off = tail_off + 16
    for _ in range(orig_lang_cnt):
        off = _skip_str(raw, off)  # language name
        off = _skip_str(raw, off)  # language code
        off += 4  # extra flags
    sync_off = off

    # Kiểm chứng khớp 100% đến cuối mảng Assets (rem == 0)
    tail_raw = raw[sync_off:]
    toff = 8
    for _ in range(4):
        toff = _skip_str(tail_raw, toff)
    toff += 16
    acnt = struct.unpack_from('<I', tail_raw, toff)[0]
    assert toff + 4 + acnt * 12 == len(tail_raw), (
        f"Parse tail I2Languages lệch byte: off={toff + 4 + acnt * 12}, len={len(tail_raw)}"
    )
    return {
        "terms_off": terms_off,
        "orig_total_terms": orig_total_terms,
        "tail_off": tail_off,
        "orig_lang_cnt": orig_lang_cnt,
        "sync_off": sync_off,
        "assets_count": acnt,
    }

def _find_i2_languages(env):
    """Tìm MonoBehaviour 'I2Languages' duy nhất theo tên và cấu trúc."""
    matches = []
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        raw = obj.get_raw_data()
        name, name_end = _read_mb_name(raw)
        if name == "I2Languages":
            terms_off = name_end + 12
            info = _parse_i2_offsets(raw, terms_off)
            matches.append((obj, raw, info))
    assert len(matches) == 1, f"Kỳ vọng đúng 1 I2Languages trong resources.assets, tìm thấy {len(matches)}"
    return matches[0]

def _find_shared0_file_id(res_env):
    """Tra fileID (1-based) của sharedassets0.assets trong externals của resources.assets."""
    for idx, ext in enumerate(res_env.file.externals, start=1):
        ext_name = os.path.basename(getattr(ext, "path", "") or getattr(ext, "name", "") or "").lower()
        if ext_name == "sharedassets0.assets" or (getattr(ext, "name", "") or "").lower() == "sharedassets0.assets":
            return idx
    raise ValueError("Không tìm thấy external 'sharedassets0.assets' trong resources.assets")

def _find_fonts_by_name(env, target_names):
    """Tra đối tượng Font và typetree theo m_Name trong serialized asset."""
    wanted = set(target_names)
    found = {}
    for obj in env.objects:
        if obj.type.name != "Font":
            continue
        tt = obj.read_typetree()
        name = tt.get("m_Name", "")
        if name in wanted:
            assert name not in found, f"Trùng tên Font '{name}'"
            found[name] = (obj, tt)
    missing = [n for n in target_names if n not in found]
    assert not missing, f"Thiếu Font: {missing}"
    return found

def _patch_tail_assets(tail_raw, extra_assets):
    """Định vị và chèn thêm PPtr vào mảng Assets ở cuối LanguageSourceData (I2Languages)."""
    off = 8  # IgnoreDeviceLanguage (4B) + _AllowUnloadingLanguages (4B)
    for _ in range(4):  # WebServiceURL, SpreadsheetKey, SpreadsheetName, LastUpdatedVersion
        off = _skip_str(tail_raw, off)
    off += 16  # GoogleUpdateFrequency, GoogleInEditorCheckFrequency, GoogleUpdateSynchronization, GoogleUpdateDelay
    assets_cnt_off = off
    cnt = struct.unpack_from('<I', tail_raw, assets_cnt_off)[0]
    assert assets_cnt_off + 4 + cnt * 12 == len(tail_raw), (
        f"Sai offset Assets trong tail: off={assets_cnt_off}, cnt={cnt}, len={len(tail_raw)}"
    )
    pptrs = [
        struct.unpack_from('<iq', tail_raw, assets_cnt_off + 4 + i * 12)
        for i in range(cnt)
    ]
    for fid, pid in extra_assets:
        if (fid, pid) not in pptrs:
            pptrs.append((fid, pid))
    out = bytearray(tail_raw[:assets_cnt_off])
    out.extend(struct.pack('<I', len(pptrs)))
    for fid, pid in pptrs:
        out.extend(struct.pack('<iq', fid, pid))
    return bytes(out)

def _parse_tmp_font_offsets(raw):
    """Parse cấu trúc nhị phân TMP_FontAsset, trả về các offset cần sửa và kiểm tra rem == 0."""
    off = 12 + 4 + 12  # m_GameObject, m_Enabled, m_Script
    off = _skip_str(raw, off)  # m_Name
    off = _skip_str(raw, off)  # m_Version
    # FaceInfo
    off += 4
    off = _skip_str(raw, off)  # familyName
    off = _skip_str(raw, off)  # styleName
    off += 8 + 4 + 60  # pt, scale, unitsPerEM, 15 float metrics
    off += 12  # m_Material
    off = _skip_str(raw, off)  # m_SourceFontFileGUID
    # FontAssetCreationSettings
    off = _skip_str(raw, off)  # sourceFontFileName
    off = _skip_str(raw, off)  # sourceFontFileGUID
    off += 36  # 9 int32 (faceIndex..characterSetSelectionMode)
    off = _skip_str(raw, off)  # characterSequence
    off = _skip_str(raw, off)  # referencedFontAssetGUID
    off = _skip_str(raw, off)  # referencedTextAssetGUID
    off += 16  # fontStyle, fontStyleModifier, renderMode, includeFontFeatures
    off += 12  # m_SourceFontFile
    off = _skip_str(raw, off)  # m_SourceFontFilePath

    pop_off = off
    pop_mode = struct.unpack_from('<i', raw, pop_off)[0]
    off += 8  # m_AtlasPopulationMode + InternalDynamicOS

    ng = struct.unpack_from('<I', raw, off)[0]
    off += 4 + ng * 52
    nc = struct.unpack_from('<I', raw, off)[0]
    off += 4 + nc * 16
    nat = struct.unpack_from('<I', raw, off)[0]
    atlas_textures = [struct.unpack_from('<iq', raw, off + 4 + i * 12) for i in range(nat)]
    off += 4 + nat * 12 + 4  # m_AtlasTextures + m_AtlasTextureIndex

    multi_off = off
    multi_atlas = struct.unpack_from('<I', raw, multi_off)[0] != 0
    off += 4 + 8 + 16  # m_IsMultiAtlasTexturesEnabled + GetFontFeatures + ClearDynamic + width/height/pad/render
    nu = struct.unpack_from('<I', raw, off)[0]
    off += 4 + nu * 16
    nf = struct.unpack_from('<I', raw, off)[0]
    off += 4 + nf * 16

    # m_FontFeatureTable
    n1 = struct.unpack_from('<I', raw, off)[0]; off += 4
    for _ in range(n1):
        off += 4
        ns = struct.unpack_from('<I', raw, off)[0]; off += 4 + ns * 4
    n2 = struct.unpack_from('<I', raw, off)[0]; off += 4
    for _ in range(n2):
        ncomp = struct.unpack_from('<I', raw, off)[0]; off += 4 + ncomp * 4 + 4
    n3 = struct.unpack_from('<I', raw, off)[0]; off += 4 + n3 * 44
    n4 = struct.unpack_from('<I', raw, off)[0]; off += 4 + n4 * 24
    n5 = struct.unpack_from('<I', raw, off)[0]; off += 4 + n5 * 24
    off += 4  # m_ShouldReimportFontFeatures

    fb_off = off
    nfb = struct.unpack_from('<I', raw, fb_off)[0]
    off += 4
    fb_list = [struct.unpack_from('<iq', raw, off + i * 12) for i in range(nfb)]
    off += nfb * 12
    after_fb_off = off

    # Kiểm chứng khớp 100% phần đuôi đến hết object (rem == 0)
    nw1 = struct.unpack_from('<I', raw, off)[0]; off += 4 + nw1 * 24
    nw2 = struct.unpack_from('<I', raw, off)[0]; off += 4 + nw2 * 24
    off += 16 + 4 + 4  # styles + italic(u8+pad) + tab(u8+pad)
    off = _skip_str(raw, off)  # m_fontInfo.Name
    off += 80
    ngl = struct.unpack_from('<I', raw, off)[0]; off += 4 + ngl * 36
    nkp = struct.unpack_from('<I', raw, off)[0]; off += 4 + nkp * 44
    nfb2 = struct.unpack_from('<I', raw, off)[0]; off += 4 + nfb2 * 12
    off += 12  # atlas
    assert off == len(raw), f"Parse TMP_FontAsset lệch byte: off={off}, len={len(raw)}"

    return {
        "pop_off": pop_off,
        "pop_mode": pop_mode,
        "multi_off": multi_off,
        "multi_atlas": multi_atlas,
        "atlas_textures": atlas_textures,
        "fb_off": fb_off,
        "after_fb_off": after_fb_off,
        "fb_list": fb_list,
    }

def _patch_tmp_font(raw, set_dynamic=False, prepend_fb=None):
    info = _parse_tmp_font_offsets(raw)
    buf = bytearray(raw)
    if set_dynamic:
        struct.pack_into('<i', buf, info["pop_off"], 1)
        struct.pack_into('<I', buf, info["multi_off"], 1)
    if prepend_fb is not None:
        new_fb = [prepend_fb] + [p for p in info["fb_list"] if p != prepend_fb]
        fb_bytes = bytearray(struct.pack('<I', len(new_fb)))
        for fid, pid in new_fb:
            fb_bytes.extend(struct.pack('<iq', fid, pid))
        out = bytes(buf[:info["fb_off"]]) + bytes(fb_bytes) + bytes(buf[info["after_fb_off"]:])
    else:
        out = bytes(buf)
    _parse_tmp_font_offsets(out)  # Xác nhận rem == 0 sau sửa
    return out

def _find_tmp_fonts_by_name(sa0_env, target_names):
    """Tìm các MonoBehaviour TMP_FontAsset theo m_Name và kiểm tra parse rem == 0."""
    wanted = set(target_names)
    found = {}
    for obj in sa0_env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        raw = obj.get_raw_data()
        name, _ = _read_mb_name(raw)
        if name in wanted:
            info = _parse_tmp_font_offsets(raw)
            assert name not in found, f"Trùng TMP_FontAsset '{name}' trong sharedassets0.assets"
            found[name] = (obj, info)
    missing = [n for n in target_names if n not in found]
    assert not missing, f"Thiếu TMP_FontAsset trong sharedassets0.assets: {missing}"
    return found

def build_resources_assets():
    terms_json = os.path.join(SRC_DIR, "raw_text", "i2languages_terms.json")
    vi_json = os.path.join(SRC_DIR, "vi_text", "i2languages_vi.json")
    output_assets = os.path.join(REPO_DIR, "dist", "build", "resources.assets")
    clean_assets = get_clean_resource_path()
    clean_sa0 = get_clean_sharedassets0_path()

    print(f"[1/2] Đóng gói resources.assets từ {clean_assets}...")
    with open(vi_json, 'r', encoding='utf-8') as f:
        vi_dict = json.load(f)
    with open(terms_json, 'r', encoding='utf-8') as f:
        terms = json.load(f)

    sa0_env = UnityPy.load(clean_sa0)
    sa0_fonts = _find_fonts_by_name(sa0_env, ("NotoSans-Bold", "NotoSans-Regular"))
    noto_bold_obj, _ = sa0_fonts["NotoSans-Bold"]
    _, noto_reg_tt = sa0_fonts["NotoSans-Regular"]

    env = UnityPy.load(clean_assets)
    sa0_file_id = _find_shared0_file_id(env)
    extra_assets = [
        (sa0_file_id, noto_bold_obj.path_id),
        (sa0_file_id, sa0_fonts["NotoSans-Regular"][0].path_id),
    ]
    obj, raw, i2_info = _find_i2_languages(env)
    nexa_heavy_obj, nexa_heavy_tt = _find_fonts_by_name(env, ("Nexa Heavy",))["Nexa Heavy"]
    orig_nexa_meta = (
        nexa_heavy_tt["m_Name"],
        dict(nexa_heavy_tt["m_DefaultMaterial"]),
        dict(nexa_heavy_tt["m_Texture"]),
        nexa_heavy_tt["m_FontSize"],
        nexa_heavy_tt["m_FontRenderingMode"],
    )

    font_mapping = {
        "Font_NexaBlack": "NotoSans-Bold",
        "Font_NexaBold": "NotoSans-Bold",
        "Font_NexaHeavy": "NotoSans-Bold",
        "Font_NexaRegular": "NotoSans-Regular",
        "Font_NexaRegularItalic": "NotoSans-Regular",
        "Font_TextMesh_Cheeseusauceu": "NotoSans-Bold SDF",
        "Font_TextMesh_NexaBlack": "NotoSans-Bold SDF",
        "Font_TextMesh_NexaBold": "NotoSans-Bold SDF",
        "Font_TextMesh_NexaHeavy": "NotoSans-Bold SDF",
        "Font_TextMesh_NexaRegular": "NotoSans-Regular SDF",
        "Font_TextMesh_NexaRegularItalic": "NotoSans-Regular SDF",
        "Font_TextMesh_Troika": "NotoSans-Bold SDF",
        "Font_Troika": "NotoSans-Bold"
    }

    terms_off = i2_info["terms_off"]
    tail_off = i2_info["tail_off"]
    orig_lang_cnt = i2_info["orig_lang_cnt"]
    sync_off = i2_info["sync_off"]

    buf = bytearray()
    # Header trước total_terms
    buf.extend(raw[:terms_off])

    # Số lượng terms
    buf.extend(struct.pack('<I', len(terms)))

    for item in terms:
        t_name = item["term"]
        t_type = item["type"]
        langs = item["langs"]  # 15 ngôn ngữ gốc
        flags = item["flags"]  # 15 flags gốc
        touch_date = item["touch_date"]

        # Xác định nội dung Tiếng Việt (Slot 16 - index 15)
        if t_name == "GEN_MENU_LANGUAGE_THIS":
            vi_str = "Tiếng Việt"
        elif t_name == "GEN_MENU_LANGUAGE_THIS_EN":
            vi_str = "Vietnamese"
        elif t_name in font_mapping:
            vi_str = font_mapping[t_name]
        elif t_name in vi_dict:
            vi_str = vi_dict[t_name]
        else:
            vi_str = langs[0]  # English fallback

        # Encode term name
        name_b = t_name.encode('utf-8')
        buf.extend(struct.pack('<I', len(name_b)))
        buf.extend(pad4(name_b))

        # Term type
        buf.extend(struct.pack('<I', t_type))

        # Lang count: orig_lang_cnt + 1 (16)
        buf.extend(struct.pack('<I', orig_lang_cnt + 1))

        # 15 original languages (Slot 0 English được bảo tồn nguyên vẹn 100%)
        for s in langs:
            sb = s.encode('utf-8')
            buf.extend(struct.pack('<I', len(sb)))
            buf.extend(pad4(sb))

        # Ngôn ngữ thứ 16: Tiếng Việt
        vib = vi_str.encode('utf-8')
        buf.extend(struct.pack('<I', len(vib)))
        buf.extend(pad4(vib))

        # Flags array: 16 bytes
        new_flags = list(flags) + [0]
        buf.extend(struct.pack('<I', len(new_flags)))
        buf.extend(pad4(bytes(new_flags)))

        # Touch date
        buf.extend(struct.pack('<I', touch_date))

    # Tail section: 12 bytes header + lang count (16) + 15 ngôn ngữ gốc + Tiếng Việt + sync/Assets
    buf.extend(raw[tail_off:tail_off + 12])
    buf.extend(struct.pack('<I', orig_lang_cnt + 1))
    buf.extend(raw[tail_off + 16:sync_off])

    vi_name_b = "Tiếng Việt".encode('utf-8')
    vi_code_b = "vi".encode('utf-8')
    buf.extend(struct.pack('<I', len(vi_name_b)))
    buf.extend(pad4(vi_name_b))
    buf.extend(struct.pack('<I', len(vi_code_b)))
    buf.extend(pad4(vi_code_b))
    buf.extend(b'\x00\x00\x00\x00')

    tail_patched = _patch_tail_assets(raw[sync_off:], extra_assets)
    buf.extend(tail_patched)

    built_raw = bytes(buf)
    _parse_i2_offsets(built_raw, terms_off)
    obj.set_raw_data(built_raw)

    # Thay dữ liệu Font 'Nexa Heavy' (ControlMapper) bằng NotoSans-Regular + fallback NotoSans-Bold
    expected_nexa_fb = [{"m_FileID": sa0_file_id, "m_PathID": noto_bold_obj.path_id}]
    nexa_heavy_tt["m_FontData"] = list(noto_reg_tt["m_FontData"])
    nexa_heavy_tt["m_FontNames"] = list(noto_reg_tt["m_FontNames"])
    nexa_heavy_tt["m_Ascent"] = noto_reg_tt["m_Ascent"]
    nexa_heavy_tt["m_Descent"] = noto_reg_tt["m_Descent"]
    nexa_heavy_tt["m_LineSpacing"] = noto_reg_tt["m_LineSpacing"]
    nexa_heavy_tt["m_KerningValues"] = []
    nexa_heavy_tt["m_CharacterRects"] = []
    nexa_heavy_tt["m_FallbackFonts"] = expected_nexa_fb
    nexa_heavy_obj.save_typetree(nexa_heavy_tt)

    os.makedirs(os.path.dirname(output_assets), exist_ok=True)
    with open(output_assets, "wb") as f:
        f.write(env.file.save())

    verify_env = UnityPy.load(output_assets)
    _, _, v_info = _find_i2_languages(verify_env)
    assert v_info["orig_total_terms"] == len(terms)
    assert v_info["orig_lang_cnt"] == orig_lang_cnt + 1

    _, v_nexa = _find_fonts_by_name(verify_env, ("Nexa Heavy",))["Nexa Heavy"]
    assert (
        v_nexa["m_Name"],
        v_nexa["m_DefaultMaterial"],
        v_nexa["m_Texture"],
        v_nexa["m_FontSize"],
        v_nexa["m_FontRenderingMode"],
    ) == orig_nexa_meta, "Font: Nexa Heavy bị sai lệch metadata gốc"
    assert v_nexa["m_FontNames"] == list(noto_reg_tt["m_FontNames"])
    assert v_nexa["m_FallbackFonts"] == expected_nexa_fb
    assert v_nexa["m_KerningValues"] == [] and v_nexa["m_CharacterRects"] == []
    assert v_nexa["m_Ascent"] == noto_reg_tt["m_Ascent"]
    assert v_nexa["m_Descent"] == noto_reg_tt["m_Descent"]
    assert v_nexa["m_LineSpacing"] == noto_reg_tt["m_LineSpacing"]
    assert list(v_nexa["m_FontData"]) == list(noto_reg_tt["m_FontData"])

    print(
        f"Đã lưu resources.assets thành công ({os.path.getsize(output_assets):,} bytes, "
        f"I2Languages#{obj.path_id}, NexaHeavy#{nexa_heavy_obj.path_id}, extra={extra_assets})."
    )
    return True

def _get_ress_path(clean_shared0_path):
    candidates = [
        os.path.join(os.path.dirname(clean_shared0_path), "sharedassets0.assets.resS"),
        os.path.join(GAME_DATA_DIR, "sharedassets0.assets.resS"),
        os.path.join(SCRIPT_DIR, "backup", "sharedassets0.assets.resS"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("Could not find sharedassets0.assets.resS!")

def build_sharedassets0_assets():
    output_assets = os.path.join(REPO_DIR, "dist", "build", "sharedassets0.assets")
    clean_assets = get_clean_sharedassets0_path()
    ress_path = _get_ress_path(clean_assets)

    dynamic_sdf_names = ("NotoSans-Bold SDF", "NotoSans-Regular SDF")
    bold_fb_names = (
        "Nexa Black SDF",
        "Nexa Bold SDF",
        "Nexa Heavy SDF",
        "NotoSansTC-Bold SDF",
        "troika SDF",
    )
    reg_fb_names = (
        "Nexa Regular Italic SDF",
        "Nexa Regular SDF",
        "NotoSansTC-Regular SDF",
    )
    all_tmp_names = dynamic_sdf_names + bold_fb_names + reg_fb_names

    print(f"[2/2] Đóng gói sharedassets0.assets từ {clean_assets} (resS: {ress_path})...")
    env = UnityPy.load(clean_assets)
    objs = {obj.path_id: obj for obj in env.objects}
    tmp_fonts = _find_tmp_fonts_by_name(env, all_tmp_names)

    atlas_tex_pids = {}
    for sdf_name in dynamic_sdf_names:
        atlases = tmp_fonts[sdf_name][1]["atlas_textures"]
        assert len(atlases) >= 1 and atlases[0][0] == 0, f"{sdf_name} có m_AtlasTextures bất thường: {atlases}"
        tex_pid = atlases[0][1]
        assert objs[tex_pid].type.name == "Texture2D", f"Atlas của {sdf_name} (#{tex_pid}) không phải Texture2D"
        atlas_tex_pids[sdf_name] = tex_pid
    assert len(set(atlas_tex_pids.values())) == len(dynamic_sdf_names), f"Trùng atlas Texture2D: {atlas_tex_pids}"

    with open(ress_path, "rb") as f_ress:
        # 1. Chuyển Texture2D atlas của NotoSans-Bold SDF và NotoSans-Regular SDF sang inline + m_IsReadable = True
        for sdf_name, tex_pid in atlas_tex_pids.items():
            tex_obj = objs[tex_pid]
            tt = tex_obj.read_typetree()
            sd = tt["m_StreamData"]
            if sd["size"] > 0:
                assert sd["size"] == 262144 and sd["path"] == "sharedassets0.assets.resS", (
                    f"Tex#{tex_pid} ({sdf_name}) stream bất thường: {sd}"
                )
                f_ress.seek(sd["offset"])
                pixels = f_ress.read(262144)
                assert len(pixels) == 262144
                raw_tex = tex_obj.get_raw_data()
                nlen = struct.unpack_from('<I', raw_tex, 0)[0]
                name_end = 4 + ((nlen + 3) // 4) * 4
                assert raw_tex[name_end + 28] == (1 if tt["m_IsReadable"] else 0)
                assert len(raw_tex) >= 48 and raw_tex[-48:-44] == b'\x00\x00\x00\x00'
                new_tex = bytearray(raw_tex[:-48] + struct.pack('<I', 262144) + pixels + b'\x00' * 16)
                new_tex[name_end + 28] = 1  # m_IsReadable = True
                tex_obj.set_raw_data(bytes(new_tex))
            elif not tt["m_IsReadable"]:
                raw_tex = bytearray(tex_obj.get_raw_data())
                nlen = struct.unpack_from('<I', raw_tex, 0)[0]
                name_end = 4 + ((nlen + 3) // 4) * 4
                assert raw_tex[name_end + 28] == 0
                raw_tex[name_end + 28] = 1
                tex_obj.set_raw_data(bytes(raw_tex))

    # 2. Chuyển NotoSans-Bold SDF / NotoSans-Regular SDF sang Dynamic + MultiAtlas (giữ pre-baked glyphs)
    for sdf_name in dynamic_sdf_names:
        obj, _ = tmp_fonts[sdf_name]
        obj.set_raw_data(_patch_tmp_font(obj.get_raw_data(), set_dynamic=True))

    bold_sdf_pid = tmp_fonts["NotoSans-Bold SDF"][0].path_id
    reg_sdf_pid = tmp_fonts["NotoSans-Regular SDF"][0].path_id

    # 3. Đưa NotoSans-Bold SDF lên đầu fallback các font Bold/Heavy/Black/Troika/TC-Bold
    for font_name in bold_fb_names:
        obj, _ = tmp_fonts[font_name]
        obj.set_raw_data(_patch_tmp_font(obj.get_raw_data(), prepend_fb=(0, bold_sdf_pid)))

    # 4. Đưa NotoSans-Regular SDF lên đầu fallback các font Regular/Italic/TC-Regular
    for font_name in reg_fb_names:
        obj, _ = tmp_fonts[font_name]
        obj.set_raw_data(_patch_tmp_font(obj.get_raw_data(), prepend_fb=(0, reg_sdf_pid)))

    os.makedirs(os.path.dirname(output_assets), exist_ok=True)
    with open(output_assets, "wb") as f:
        f.write(env.file.save())

    # Kiểm chứng lại từ file vừa ghi trên đĩa (UnityPy chỉ cập nhật reader sau khi save)
    verify_env = UnityPy.load(output_assets)
    v_objs = {o.path_id: o for o in verify_env.objects}
    v_fonts = _find_tmp_fonts_by_name(verify_env, all_tmp_names)
    for sdf_name in dynamic_sdf_names:
        _, v_info = v_fonts[sdf_name]
        assert v_info["pop_mode"] == 1 and v_info["multi_atlas"] is True, f"{sdf_name} chưa bật Dynamic+MultiAtlas"
        tex_pid = v_info["atlas_textures"][0][1]
        assert tex_pid == atlas_tex_pids[sdf_name]
        tt_chk = v_objs[tex_pid].read_typetree()
        assert tt_chk["m_IsReadable"] is True, f"Tex#{tex_pid} m_IsReadable vẫn False"
        assert len(tt_chk["image data"]) == 262144, f"Tex#{tex_pid} image data != 262144"
        assert tt_chk["m_StreamData"] == {"offset": 0, "size": 0, "path": ""}, f"Tex#{tex_pid} m_StreamData chưa rỗng"
    for font_name in bold_fb_names:
        assert v_fonts[font_name][1]["fb_list"][0] == (0, bold_sdf_pid), f"{font_name} fallback đầu sai"
    for font_name in reg_fb_names:
        assert v_fonts[font_name][1]["fb_list"][0] == (0, reg_sdf_pid), f"{font_name} fallback đầu sai"

    print(
        f"Đã lưu sharedassets0.assets thành công ({os.path.getsize(output_assets):,} bytes, "
        f"BoldSDF=#{bold_sdf_pid}, RegSDF=#{reg_sdf_pid}, Atlas={atlas_tex_pids})."
    )
    return True

def install_to_game():
    if not os.path.exists(GAME_DATA_DIR):
        print(f"[!] Khong tim thay thu muc game: {GAME_DATA_DIR}")
        return False
    
    os.makedirs(BACKUP_DIR, exist_ok=True)
    import shutil
    # 1. Sao lưu file gốc nếu chưa có
    for asset_name in ("resources.assets", "sharedassets0.assets"):
        orig_file = os.path.join(GAME_DATA_DIR, asset_name)
        backup_file = os.path.join(BACKUP_DIR, asset_name)
        if os.path.exists(orig_file) and not os.path.exists(backup_file):
            shutil.copy2(orig_file, backup_file)
            print(f"[Sao lưu] Đã sao lưu {asset_name} gốc sạch vào {BACKUP_DIR}")

    # 2. Copy mod build vào game
    res_mod = os.path.join(REPO_DIR, "dist", "build", "resources.assets")
    sa0_mod = os.path.join(REPO_DIR, "dist", "build", "sharedassets0.assets")
    if os.path.exists(res_mod):
        shutil.copy2(res_mod, os.path.join(GAME_DATA_DIR, "resources.assets"))
        print("[Cài đặt] Đã chép resources.assets (Tiếng Việt) vào game!")
    if os.path.exists(sa0_mod):
        shutil.copy2(sa0_mod, os.path.join(GAME_DATA_DIR, "sharedassets0.assets"))
        print("[Cài đặt] Đã chép sharedassets0.assets (Font SDF) vào game!")

    # 3. Kích hoạt Registry tiếng Việt
    try:
        import winreg
        key_path = r"Software\Pajama Llama Games\Flotsam"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        val_bytes = bytes.fromhex("5469e1babf6e67205669e1bb877400")
        winreg.SetValueEx(key, "I2 Language_h3293684300", 0, winreg.REG_BINARY, val_bytes)
        winreg.CloseKey(key)
        print("[Registry] Đã kích hoạt mặc định 'Tiếng Việt' trong Registry Windows!")
    except Exception as e:
        print(f"[Registry] Lưu ý: {e}")

    print("\n=======================================================")
    print("  ĐÃ CÀI ĐẶT THÀNH CÔNG BẢN VIỆT HÓA VÀO GAME FLOTSAM! ")
    print("  Bạn có thể khởi động game từ Epic Games Launcher ngay!")
    print("=======================================================\n")
    return True

def build(install=True):
    print("=== BẮT ĐẦU ĐÓNG GÓI BẢN PATCH VIỆT HÓA FLOTSAM TỪ SRC ===")
    build_resources_assets()
    build_sharedassets0_assets()
    print("=== HOÀN TẤT ĐÓNG GÓI THÀNH CÔNG ===")
    if install:
        install_to_game()
    return True

if __name__ == "__main__":
    build_only = "--build-only" in sys.argv
    build(install=not build_only)