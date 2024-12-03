import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from DataGenerator import *
from Clustering import *

# App: Xây dựng giao diện ứng dụng
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Phân Cụm Sản Phẩm")
        self.root.geometry("900x600")  # Đặt kích thước cửa sổ cố định
        
        # Căn giữa màn hình khi khởi động
        window_width = 900
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_left = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')
        
        self.data_generator = DataGenerator()
        self.clustering = None  # Clustering sẽ được tạo khi người dùng chọn số cụm
        self.data = None
        self.sort_column = None  # Cột hiện tại được sắp xếp
        self.sort_reverse = False  # Trạng thái sắp xếp (True: giảm dần, False: tăng dần)
        
        # Cấu hình style cho các widget
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10), padding=6)
        self.style.configure("TLabel", font=("Arial", 10))
        
        self.setup_ui()

    def setup_ui(self):
        # Thanh điều hướng (Menu bar)
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Tệp", menu=file_menu)
        file_menu.add_command(label="Tải dữ liệu CSV", command=self.load_file)
        file_menu.add_command(label="Lưu dữ liệu CSV", command=self.save_file)
        
        # Khung các nút chức năng
        action_frame = ttk.Frame(self.root, padding="10")
        action_frame.pack(fill=tk.X, padx=20, pady=10)

        # Các nút chức năng
        btn_random_100 = ttk.Button(action_frame, text="Random 100 sản phẩm", command=self.random_100)
        btn_random_100.pack(side=tk.LEFT, padx=10)

        btn_random_10 = ttk.Button(action_frame, text="Random 10 sản phẩm", command=self.random_10)
        btn_random_10.pack(side=tk.LEFT, padx=10)

        # Nhập số lượng cụm
        ttk.Label(action_frame, text="Số cụm:").pack(side=tk.LEFT, padx=10)
        self.cluster_entry = ttk.Entry(action_frame, width=5)
        self.cluster_entry.pack(side=tk.LEFT, padx=10)

        btn_cluster = ttk.Button(action_frame, text="Phân cụm", command=self.cluster_data)
        btn_cluster.pack(side=tk.LEFT, padx=10)

        btn_save_result = ttk.Button(action_frame, text="Lưu kết quả CSV", command=self.save_result)
        btn_save_result.pack(side=tk.LEFT, padx=10)
        
        btn_suggest = ttk.Button(action_frame, text="Gợi ý sản phẩm tốt nhất", command=self.suggest_best_products)
        btn_suggest.pack(side=tk.LEFT, padx=10)

        # Bảng hiển thị dữ liệu
        columns = ["id", "name", "category", "brand", "rating", "review_count", "cluster"]
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tree_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", yscrollcommand=self.tree_scroll.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree_scroll.config(command=self.tree.yview)
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=120, anchor=tk.CENTER)
        
        # Thanh trạng thái
        self.status_bar = ttk.Label(self.root, text="Chào mừng bạn đến với Phân Cụm Sản Phẩm!", relief=tk.SUNKEN, anchor=tk.W, background="lightblue", padding=(10, 5))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def random_100(self):
        self.data = self.data_generator.random_product(100)
        self.display_data(self.data)
        self.update_status("Dữ liệu ngẫu nhiên 100 sản phẩm đã được tạo.")

    def random_10(self):
        self.data = self.data_generator.random_product(10)
        self.display_data(self.data)
        self.update_status("Dữ liệu ngẫu nhiên 10 sản phẩm đã được tạo.")

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.data = pd.read_csv(file_path).to_dict('records')
            self.display_data(self.data)
            self.update_status(f"Đã tải dữ liệu từ {file_path}.")

    def save_file(self):
        if self.data:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                df = pd.DataFrame(self.data)
                df.to_csv(file_path, index=False)
                self.update_status(f"Dữ liệu đã được lưu tại {file_path}.")

    def cluster_data(self):
        if not self.data:
            messagebox.showerror("Lỗi", "Chưa có dữ liệu để phân cụm!")
            return

        # Gọi hàm tiền xử lý
        df = self.preprocess_data()
        if df is None or df.empty:
            messagebox.showerror("Lỗi", "Không đủ dữ liệu hợp lệ để phân cụm!")
            return

        try:
            # Lấy số cụm từ người dùng
            n_clusters = int(self.cluster_entry.get())
            if n_clusters < 1:
                raise ValueError("Số cụm phải lớn hơn 0.")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số cụm hợp lệ.")
            return
        
        # Khởi tạo Clustering và phân cụm
        self.clustering = Clustering(n_clusters=n_clusters)
        df = self.clustering.fit_predict(self.data)
        
        # Cập nhật dữ liệu với nhãn cụm
        self.data = df.to_dict("records")
        self.display_data(self.data)
        self.display_clusters(df)
        self.update_status(f"Đã phân cụm với {n_clusters} cụm.")

    def save_result(self):
        if self.data:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                df = pd.DataFrame(self.data)
                df.to_csv(file_path, index=False)
                self.update_status(f"Kết quả đã được lưu tại {file_path}.")

    def display_data(self, data):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in data:
            self.tree.insert("", "end", values=list(row.values()))

    def sort_by_column(self, column):
        if column != "cluster":
            return
        if not self.data:
            return
        self.sort_reverse = (self.sort_column == column and not self.sort_reverse)  # Đổi chiều sắp xếp
        self.sort_column = column
        self.data = sorted(self.data, key=lambda x: x[column], reverse=self.sort_reverse)
        self.display_data(self.data)

    def display_clusters(self, df):
        # Hiển thị biểu đồ phân cụm
        fig, ax = plt.subplots(figsize=(6, 4))
        scatter = ax.scatter(
            df["rating"], df["review_count"], c=df["cluster"], cmap="viridis"
        )
        ax.set_xlabel("Đánh giá trung bình")
        ax.set_ylabel("Số lượng đánh giá")
        plt.colorbar(scatter, ax=ax)

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.get_tk_widget().pack(pady=10)
        canvas.draw()

    def update_status(self, message):
        self.status_bar.config(text=message)

    def preprocess_data(self):
        if not self.data:
            messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu để xử lý!")
            return None

        # Chuyển đổi dữ liệu sang DataFrame
        df = pd.DataFrame(self.data)
        
        # Loại bỏ các hàng có giá trị thiếu
        initial_len = len(df)
        df = df.dropna()
        removed_rows = initial_len - len(df)

        # Kiểm tra và cảnh báo nếu có giá trị bị loại bỏ
        if removed_rows > 0:
            messagebox.showinfo("Thông báo", f"Đã loại bỏ {removed_rows} dòng dữ liệu thiếu!")

        # Chuyển đổi các cột không phải số (nếu cần)
        numeric_columns = ["rating", "review_count"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Loại bỏ giá trị không hợp lệ (vd: NaN sau chuyển đổi)
        df = df.dropna(subset=numeric_columns)

        # Cập nhật lại dữ liệu sau khi xử lý
        self.data = df.to_dict("records")
        return df

    def suggest_best_products(self):
        if not self.data or not self.clustering:
            messagebox.showerror("Lỗi", "Chưa có dữ liệu hoặc chưa phân cụm!")
            return

        # Chuyển dữ liệu sang DataFrame
        df = pd.DataFrame(self.data)

        # Tính toán rating trung bình và tổng review_count cho từng cụm
        cluster_stats = df.groupby("cluster").agg(
            avg_rating=("rating", "mean"),
            total_reviews=("review_count", "sum")
        )

        # Xác định cụm có rating cao nhất và review lớn nhất
        best_rating_cluster = cluster_stats["avg_rating"].idxmax()
        most_reviewed_cluster = cluster_stats["total_reviews"].idxmax()

        # Lọc sản phẩm từ cụm tốt nhất (rating cao nhất hoặc nhiều review nhất)
        suggested_products = df[df["cluster"].isin([best_rating_cluster, most_reviewed_cluster])]

        # Hiển thị gợi ý trong TreeView
        self.display_data(suggested_products.to_dict("records"))
        self.update_status("Hiển thị sản phẩm từ các cụm tốt nhất.")

# Khởi chạy ứng dụng
root = tk.Tk()
app = App(root)
root.mainloop()