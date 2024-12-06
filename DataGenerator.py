import random
import csv
import os
from datetime import datetime

class DataGenerator:
    def __init__(self):
        self.categories = ["Laptop", "Điện thoại", "Tablet", "PC"]
        self.brands = ["Apple", "Samsung", "Dell", "HP", "Asus", "Lenovo"]
        self.phone_names = ["iPhone", "Samsung Galaxy", "Xiaomi Mi", "Oppo Reno", "Vivo X"]
        self.laptop_names = ["MacBook", "Dell XPS", "HP Spectre", "Lenovo ThinkPad", "Asus ZenBook"]
        self.tablet_names = ["iPad", "Samsung Galaxy Tab", "Microsoft Surface", "Huawei MatePad"]
        self.pc_names = ["HP Pavilion", "Dell Inspiron", "Lenovo IdeaPad", "Asus ROG"]

    def create_data_folder(self):
        # Kiểm tra nếu thư mục "data" đã tồn tại
        if not os.path.exists("data"):
            os.makedirs("data")
        
        # Tạo thư mục mới với tên dạng folder_X_YYYY-MM-DD_HH-MM
        folder_name = f"data/folder_{len(os.listdir('data')) + 1}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        os.makedirs(folder_name)
        
        return folder_name

    def random_product(self, n=100, save_reviews=False):
        folder_name = self.create_data_folder()  # Tạo thư mục chứa dữ liệu
        products = []
        
        for i in range(1, n + 1):
            category = random.choice(self.categories)
            brand = random.choice(self.brands)
            if category == "Điện thoại":
                model = f"{random.choice(self.phone_names)} {random.randint(10, 100)} {random.choice(['Pro', 'Max', 'Ultra', 'Lite'])}"
            elif category == "Laptop":
                model = f"{random.choice(self.laptop_names)} {random.choice(['2023', '2024', 'Pro', 'Ultra'])}"
            elif category == "Tablet":
                model = f"{random.choice(self.tablet_names)} {random.randint(7, 12)}"
            else:  # PC
                model = f"{random.choice(self.pc_names)} {random.randint(15, 30)}"

            # Xác suất để quyết định rating cao, trung bình, thấp
            rating_group = random.choices(["high", "medium", "low"], weights=[0.3, 0.4, 0.3], k=1)[0]
            
            # Chọn số lượng đánh giá
            review_count = random.randint(1, 500)
            
            # Tạo đánh giá theo nhóm rating
            if rating_group == "high":
                reviews = [random.randint(4, 5) for _ in range(review_count)]  # Đánh giá cao
                rating = round(sum(reviews) / len(reviews), 1)
            elif rating_group == "medium":
                reviews = [random.randint(3, 4) for _ in range(review_count)]  # Đánh giá trung bình
                rating = round(sum(reviews) / len(reviews), 1)
            else:
                reviews = [random.randint(1, 2) for _ in range(review_count)]  # Đánh giá thấp
                rating = round(sum(reviews) / len(reviews), 1)

            # Lưu danh sách đánh giá vào thư mục chứa dữ liệu
            if save_reviews:
                filename = os.path.join(folder_name, f"product_{i}_reviews.csv")
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Review"])  # Header
                    for review in reviews:
                        writer.writerow([review])

            # Thêm sản phẩm vào danh sách
            products.append({
                "id": i,
                "name": model,
                "category": category,
                "brand": brand,
                "rating": rating,  # Làm tròn đến chữ số thập phân thứ nhất
                "review_count": review_count
            })

        return products
