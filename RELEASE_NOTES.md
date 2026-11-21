# Flotsam — Bản Dịch Tiếng Việt v1.0.0

Bản dịch tiếng Việt hoàn chỉnh dành cho tựa game sinh tồn xây dựng trên biển **Flotsam** (Pajama Llama Games / Unity 6 Mono x64).

---

## Thông tin bản phát hành v1.0.0

- **Phiên bản trò chơi hỗ trợ:** v1.1.0f5 (Epic Games Store).
- **Quy mô dữ liệu:** Hoàn tất 100% với 3.263 / 3.263 chuỗi văn bản gồm Giao diện, Menu cài đặt, Công trình sản xuất, Cây nghiên cứu, Cư dân, Tài nguyên, Cẩm nang sinh tồn, Hội thoại NPC và Nhiệm vụ cốt truyện.
- **Cơ chế Pure Asset Localization:** Giữ nguyên 100% mã nguồn thực thi `Assembly-CSharp.dll` gốc sạch của nhà phát triển (Zero Code Change) và các tệp màn chơi `level*`. Bổ sung slot ngôn ngữ thứ 16 ("Tiếng Việt", mã `vi`) vào hệ thống I2 Localization trong `resources.assets`.
- **Xử lý font chữ:** Tích hợp font SDF tiếng Việt chuẩn `NotoSans-Bold SDF` vào `sharedassets0.assets` và 4 bộ font vector phụ trợ, loại bỏ hoàn toàn lỗi hiển thị ký tự và ô vuông.
- **Kịch bản cài đặt tự động:** Kèm tệp `Cai_Dat_Viet_Hoa.bat` tự động sao lưu tệp gốc và triển khai bản patch trong một thao tác.

---

## Lưu ý nhỏ

- **Miễn phí 100%:** Bản Việt hóa được thực hiện và chia sẻ miễn phí bởi **[Diiexe](https://github.com/diiexe)**. Nếu bạn phải bỏ tiền mua bản dịch này ở bất kỳ đâu thì bạn đã bị lừa đảo.
- **Bản dịch bằng AI** mình làm để tự chơi cá nhân, tiện chia sẻ lại cho ai cần. Dùng được thì dùng, không dùng thì thôi nhé.
- **Miễn trừ trách nhiệm:** Bản mod chỉ thêm ngôn ngữ và phông chữ, mở toàn bộ mã nguồn trên repo. Vì là bản chia sẻ cá nhân phi thương mại nên mình cung cấp theo nguyên trạng, không bảo hành và không chịu trách nhiệm nếu có lỗi phát sinh trong quá trình sử dụng.

---

## Hướng dẫn cài đặt & Gỡ bỏ

1. Tải gói phát hành `Flotsam_VietHoa_v1.0.0.zip` đính kèm bên dưới và giải nén ra bất kỳ đâu.
2. Nhấp đúp chạy `Cai_Dat_Viet_Hoa.bat`.
3. Nhập `1` và nhấn **Enter** để cài đặt (hoặc nhập `2` để gỡ bỏ, khôi phục về bản gốc sạch).
4. Mở game và trải nghiệm tiếng Việt.

---

## Chú thích tương thích phiên bản

- Phiên bản thử nghiệm cũ hơn v1.1.0f5 có cấu trúc metadata và PathID khác biệt, cài đặt gói asset có thể gây lỗi nạp ngôn ngữ.
- Khi game cập nhật bản mới từ Epic Games Launcher, launcher có thể tải lại file gốc đè lên bản patch; người dùng chỉ cần chạy lại `Cai_Dat_Viet_Hoa.bat` hoặc build lại asset bằng script đi kèm.

---

## Mã kiểm tra tính toàn vẹn (SHA-256)

| Tên tệp tin | Mã băm SHA-256 |
| :--- | :--- |
| `VietHoa_Flotsam_Full.zip` | `14fcbaedf606472dd343910630c75d8c549b387ff10d6df4764d0b0d2426aa13` |
| `resources.assets` | `a0aa72b2a77242255060355aa886d5352b99b6556af36ca96c53bc53d27317cb` |
| `sharedassets0.assets` | `1f27dc935ab32396c05dd8adad9894d9c68d3dc98dcbfd750d93b8589ad7adef` |
| `Assembly-CSharp.dll` (gốc sạch) | `5b5c9f730ed71d5f66c0267064fc57667d2ff5644a018e9189b140ce025c1cd8` |

---

## Tác giả & Bản quyền

- **Bản dịch Tiếng Việt & Bộ công cụ mã nguồn:** Thực hiện bởi **[Diiexe](https://github.com/diiexe)** (chia sẻ phi thương mại).
- **Bản quyền trò chơi gốc:** Toàn bộ hình ảnh, âm thanh, mã nguồn và tài sản trò chơi gốc thuộc về **Pajama Llama Games**.
