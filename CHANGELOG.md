# Nhật Ký Thay Đổi (Changelog)

Toàn bộ các cập nhật của dự án bản địa hóa **Flotsam** được ghi nhận tại đây.

---

## [v1.0.0] - 2026-11-21

### Phiên bản phát hành đầu tiên

#### Dữ liệu dịch thuật
- Hoàn thành dịch thuật 100% (3.263 / 3.263 chuỗi văn bản) cho phiên bản chính thức **v1.1.0f5** (Epic Games Store).
- Chuẩn hóa toàn bộ thuật ngữ sinh tồn biển, xây dựng, lọc nước, khử muối, điện phân và chế tạo trong tệp `glossary.json`.
- Hoàn thiện 47 danh xưng chức nghiệp thuần Việt cho cư dân, bảo toàn nguyên vẹn 100% họ tên riêng.
- Bản địa hóa toàn bộ lời thoại NPC Sammy Flottington và hệ thống nhiệm vụ cốt truyện.
- Loại bỏ các từ Hán-Việt tối nghĩa để câu văn tự nhiên, mộc mạc.

#### Kỹ thuật và Tương thích
- Triển khai theo mô hình Pure Asset Localization: Zero Code Change trên `Assembly-CSharp.dll` và Zero Scene Modification trên các tệp `level*`.
- Bổ sung slot ngôn ngữ thứ 16 ("Tiếng Việt", mã `vi`) vào hệ thống I2 Localization (`LanguageSourceData` trong `resources.assets`).
- Tích hợp font SDF `NotoSans-Bold SDF` có đầy đủ ký tự tiếng Việt vào PathID 2979 của `sharedassets0.assets` và 4 font vector phụ trợ.
- Kèm kịch bản `Cai_Dat_Viet_Hoa.bat` tự động sao lưu và khôi phục game gốc an toàn qua `Go_Cai_Dat.bat`.
