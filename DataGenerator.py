import random

# DataGenerator: Tạo dữ liệu ngẫu nhiên
class DataGenerator:
    def __init__(self):
        self.categories = ["Laptop", "Điện thoại", "Tablet", "PC"]
        self.brands = ["Apple", "Samsung", "Dell", "HP", "Asus", "Lenovo"]
        
        # Tạo danh sách tên sản phẩm theo cấu trúc phổ biến
        self.phone_names = ["iPhone", "Samsung Galaxy", "Xiaomi Mi", "Oppo Reno", "Vivo V"]
        self.laptop_names = ["MacBook", "Dell XPS", "HP Spectre", "Lenovo ThinkPad", "Asus ZenBook"]
        self.tablet_names = ["iPad", "Samsung Galaxy Tab", "Microsoft Surface", "Huawei MediaPad"]
        self.pc_names = ["HP Pavilion", "Dell Inspiron", "Lenovo IdeaPad", "Asus ROG"]

    def random_product(self, n=100):
        products = []
        for i in range(1, n + 1):
            category = random.choice(self.categories)
            brand = random.choice(self.brands)
            
            # Tạo tên sản phẩm hấp dẫn dựa trên thể loại
            if category == "Điện thoại":
                model = f"{random.choice(self.phone_names)} {random.randint(10, 100)} {random.choice(['Pro', 'Max', 'Ultra', 'Lite'])}"
            elif category == "Laptop":
                model = f"{random.choice(self.laptop_names)} {random.choice(['2023', '2024', 'Pro', 'Ultra'])}"
            elif category == "Tablet":
                model = f"{random.choice(self.tablet_names)} {random.randint(7, 12)}"
            else:  # PC
                model = f"{random.choice(self.pc_names)} {random.randint(15, 30)}"
                
            rating = round(random.uniform(1, 5), 1)  # Đánh giá từ 1.0 đến 5.0
            review_count = random.randint(1, 500)
            
            # Thêm sản phẩm vào danh sách
            products.append({
                "id": i,
                "name": model,
                "category": category,
                "brand": brand,
                "rating": rating,
                "review_count": review_count
            })
        return products
