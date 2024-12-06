import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.patches import Patch
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
        self.canvas = None
        self.clustering = None  # Clustering sẽ được tạo khi người dùng chọn số cụm
        self.data = None
        self.sort_column = None  # Cột hiện tại được sắp xếp
        self.sort_reverse = False  # Trạng thái sắp xếp (True: giảm dần, False: tăng dần)
        
        # Cấu hình style cho các widget
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Inter", 10), padding=6)
        self.style.configure("TLabel", font=("Inter", 10))
        self.style.configure("TTreeview", font=("Inter", 10))  # Đặt font cho Treeview
        self.style.configure("TEntry", font=("Inter", 10))  # Đặt font cho Entry
        self.style.configure("TScrollbar", font=("Inter", 10))  # Đặt font cho Scrollbar
        
        self.setup_ui()

    def setup_ui(self):
        # Thanh điều hướng (Menu bar)
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Tải dữ liệu CSV", command=self.load_file)
        file_menu.add_command(label="Lưu dữ liệu CSV", command=self.save_file)
        file_menu.add_command(label="Reset", command=self.reset_screen)

        # Thanh trạng thái - Do cấu trúc pack - Theo thứ tự 
        self.status_bar = ttk.Label(self.root, text="Chào mừng bạn đến với Phân Cụm Sản Phẩm!", relief=tk.SUNKEN, anchor=tk.W, background="lightblue", padding=(10, 5))
        self.status_bar.pack(side=tk.TOP, fill=tk.X)

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

        # Thêm nút để hiển thị đánh giá chi tiết
        btn_show_reviews = ttk.Button(action_frame, text="Xem đánh giá chi tiết", command=self.show_reviews)
        btn_show_reviews.pack(side=tk.LEFT, padx=10)

        btn_save_result = ttk.Button(action_frame, text="Lưu kết quả CSV", command=self.save_result)
        btn_save_result.pack(side=tk.LEFT, padx=10)

        # Bảng hiển thị dữ liệu
        columns = ["id", "name", "category", "brand", "rating", "review_count", "cluster", "quality"]
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

    def random_100(self):
        self.data = self.data_generator.random_product(100, save_reviews=True)
        self.display_data(self.data)
        self.update_status("Dữ liệu ngẫu nhiên 100 sản phẩm và các đánh giá đã được tạo.")

    def random_10(self):
        self.data = self.data_generator.random_product(10, save_reviews=True)
        self.display_data(self.data)
        self.update_status("Dữ liệu ngẫu nhiên 10 sản phẩm và các đánh giá đã được tạo.")

    def load_file(self):
        """Tải dữ liệu CSV từ file."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                # Đọc dữ liệu từ file CSV
                self.data = []
                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Chuyển đổi dữ liệu cho đúng kiểu
                        row["id"] = int(row["id"])
                        row["rating"] = float(row["rating"])
                        row["review_count"] = int(row["review_count"])
                        self.data.append(row)

                self.display_data(self.data)
                self.update_status(f"Đã tải dữ liệu từ {file_path}.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file: {str(e)}")

    def save_file(self):
        """Lưu dữ liệu hiển thị vào file CSV."""
        if not self.data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để lưu!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                    writer.writeheader()
                    writer.writerows(self.data)

                self.update_status(f"Dữ liệu đã được lưu tại {file_path}.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {str(e)}")

    def show_reviews(self):
        """Hiển thị đánh giá chi tiết của sản phẩm được chọn."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Lỗi", "Vui lòng chọn một sản phẩm để xem đánh giá chi tiết!")
            return

        # Lấy ID sản phẩm
        item_data = self.tree.item(selected_item)
        product_id = item_data["values"][0]

        # Xác định đường dẫn file đánh giá
        folder_name = os.listdir("data")[-1]  # Lấy thư mục dữ liệu mới nhất
        review_file = os.path.join("data", folder_name, f"product_{product_id}_reviews.csv")

        try:
            # Đọc dữ liệu từ file CSV
            reviews = []
            with open(review_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)  # Bỏ qua tiêu đề
                reviews = [row[0] for row in reader]

            # Hiển thị đánh giá trong cửa sổ pop-up
            review_window = tk.Toplevel(self.root)
            review_window.title(f"Đánh giá chi tiết - Sản phẩm ID {product_id}")
            review_window.geometry("400x300")

            ttk.Label(review_window, text=f"Danh sách đánh giá chi tiết (ID: {product_id})", font=("Inter", 12, "bold")).pack(pady=10)
            text_widget = tk.Text(review_window, wrap=tk.WORD, font=("Inter", 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            for review in reviews:
                text_widget.insert(tk.END, f"{review}\n")

            text_widget.config(state=tk.DISABLED)
        except FileNotFoundError:
            messagebox.showerror("Lỗi", f"Không tìm thấy đánh giá cho sản phẩm ID {product_id}.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc dữ liệu đánh giá: {str(e)}")

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
        
        # Thêm cột đánh giá chất lượng
        df["quality"] = df["rating"].apply(
            lambda x: "Tốt" if x > 4 else ("Trung bình" if 3 <= x <= 4 else "Kém")
        )
        
        # Xác định cụm tốt nhất
        cluster_stats = df.groupby("cluster").agg(
            avg_rating=("rating", "mean"),
            total_reviews=("review_count", "sum")
        ).reset_index()
        
        # Lọc ra cụm tốt nhất (cụm có rating trung bình cao nhất và thuộc nhóm "Tốt")
        good_clusters = cluster_stats[cluster_stats["avg_rating"] > 4]
        if not good_clusters.empty:
            best_cluster = good_clusters.loc[good_clusters["avg_rating"].idxmax()]
            best_cluster_id = int(best_cluster["cluster"])
            avg_rating = best_cluster["avg_rating"]
            total_reviews = best_cluster["total_reviews"]
            
            # Cập nhật status bar với thông tin cụm tốt nhất
            self.update_status(
                f"Gợi ý sản phẩm từ cụm tốt nhất (Cụm {best_cluster_id}): "
                f"Rating trung bình = {avg_rating:.2f}, Tổng số đánh giá = {total_reviews}."
            )
        else:
            # Trường hợp không có cụm "Tốt"
            self.update_status("Không có cụm nào thuộc nhóm 'Tốt'.")
        
        # Cập nhật dữ liệu với nhãn cụm và chất lượng
        self.data = df.to_dict("records")
        self.display_data(self.data)
        self.display_clusters(df)

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
        # Xóa biểu đồ cũ (nếu có)
        for widget in self.tree_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()

        # Hiển thị biểu đồ phân cụm
        fig, ax = plt.subplots(figsize=(8, 6))  # Tăng kích thước biểu đồ
        scatter = ax.scatter(
            df["rating"], df["review_count"], c=df["cluster"], cmap="viridis", s=50
        )
        
        # Gắn nhãn cho trục
        ax.set_xlabel("Đánh giá trung bình")
        ax.set_ylabel("Số lượng đánh giá")
        ax.set_title("Biểu đồ phân cụm sản phẩm")

        # Tạo chú thích (legend)
        clusters = df["cluster"].unique()
        legend_labels = [Patch(color=scatter.cmap(scatter.norm(c)), label=f"Cụm {int(c)}") for c in clusters]
        ax.legend(
            handles=legend_labels, 
            title="Cụm", 
            bbox_to_anchor=(1.05, 1),  # Đặt chú thích bên ngoài biểu đồ
            loc="upper left", 
            borderaxespad=0
        )

        # Điều chỉnh khoảng cách để không gian biểu đồ và chú thích không bị chèn lên nhau
        fig.subplots_adjust(right=0.8)

        # Hiển thị biểu đồ trên giao diện Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.tree_frame)
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

    def reset_screen(self):
        # Xóa dữ liệu và các phần hiển thị
        self.data = None
        self.clustering = None
        self.cluster_entry.delete(0, tk.END)  # Xóa nhập liệu số cụm
        self.update_status("Màn hình đã được làm mới.")
        
        # Xóa tất cả các dòng trong Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

# Khởi chạy ứng dụng
root = tk.Tk()
app = App(root)
root.mainloop()