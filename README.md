---------- HƯỚNG DẪN SỬ DỤNG ----------

1. Paste Script sau vào terminal "pip install -r requirements.txt" => Để tải các thư viện cần thiết
2. Chạy file App.py để sử dụng
3. Các file đều có docstring

"### Thuật toán K-Means ###\n\n"
"1. **Mục đích**: Phân nhóm dữ liệu thành các cụm dựa trên sự tương đồng.\n\n"
"2. **Cách hoạt động**:\n"
" - a. Chọn ngẫu nhiên K tâm cụm (centroids).\n"
" - b. Gán từng điểm dữ liệu vào cụm gần nhất dựa trên khoảng cách (ví dụ: Euclidean distance).\n"
" - c. Cập nhật tâm cụm bằng cách tính trung bình của các điểm trong cụm.\n"
" - d. Lặp lại bước (b) và (c) cho đến khi tâm cụm không thay đổi (hoặc đạt điều kiện dừng).\n\n"
"3. **Công thức**:\n"
" - Khoảng cách Euclidean: sqrt((x2 - x1)^2 + (y2 - y1)^2).\n\n"
"4. **Biểu diễn trực quan**: Mỗi cụm được thể hiện bằng một màu khác nhau trên biểu đồ scatter plot.\n\n"
"### Cách sử dụng ứng dụng ###\n\n"
"- **Bước 1**: Random dữ liệu hoặc tải file CSV chứa dữ liệu sản phẩm.\n"
"- **Bước 2**: Nhập số cụm K và nhấn 'Phân cụm'.\n"
"- **Bước 3**: Quan sát kết quả trên bảng và biểu đồ.\n"
"- **Bước 4**: Lưu kết quả nếu cần.\n\n"

--- Nguyễn Minh Quân ---
