import os
import math
import random
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter
from PIL import Image, ImageDraw
from PIL.Image import Resampling
from fpdf import FPDF


class DobbleGenerator:
    """
    Handles the logic for generating Dobble-like cards, processing images,
    and creating the final PDF.
    """

    def __init__(self):
        self.stop_event = threading.Event()

    @staticmethod
    def calculate_n(k):
        """
        Calculates the maximum order 'n' such that n^2 - n + 1 <= k.
        """
        n = 2
        while n**2 - n + 1 <= k:
            n += 1
        return n - 1

    @staticmethod
    def calculate_total_symbols(n):
        return n**2 - n + 1

    def load_images(self, folder):
        """
        Loads images from a folder, makes background transparent, and shuffles them.
        """
        images = []
        valid_extensions = ('.png', '.jpg', '.jpeg')
        for filename in os.listdir(folder):
            if filename.lower().endswith(valid_extensions):
                try:
                    img = Image.open(os.path.join(folder, filename))
                    img = self.convert_background_transparent(img)
                    images.append(img)
                except Exception as e:
                    print(f"Error loading image {filename}: {e}")
        random.shuffle(images)
        return images

    @staticmethod
    def convert_background_transparent(img):
        """
        Converts white/near-white background to transparent.
        """
        img = img.convert("RGBA")
        datas = img.getdata()

        new_data = []
        for item in datas:
            # Check for near-white color
            if item[0] >= 240 and item[1] >= 240 and item[2] >= 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        img.putdata(new_data)
        return img

    def generate_structure(self, symbols_per_card):
        """
        Generates the mathematical structure of Dobble cards using projective plane logic.
        """
        prime_n = symbols_per_card - 1
        total_cards = (prime_n**2) + prime_n + 1
        
        cards = []
        t = []
        
        t.append([[(i+1)+(j*prime_n) for i in range(prime_n)] for j in range(prime_n)])
        for ti in range(prime_n-1):
            t.append([[t[0][((ti+1)*i) % prime_n][(j+i) % prime_n] for i in range(prime_n)] for j in range(prime_n)])
        t.append([[t[0][i][j] for i in range(prime_n)] for j in range(prime_n)])
        
        for i in range(prime_n):
            t[0][i].append(total_cards - prime_n)
            t[prime_n][i].append(total_cards - prime_n + 1)
            for ti in range(prime_n-1):
                t[ti+1][i].append(total_cards - prime_n + 1 + ti + 1)
        t.append([[(i+(total_cards-prime_n)) for i in range(symbols_per_card)]])
        
        for ti in t:
            for card in ti:
                # Modulo to keep indices in range
                card = [symbol % total_cards for symbol in card]
                cards.append(card)
        return cards

    @staticmethod
    def get_positions(num_symbols, size, symbol_size):
        """
        Calculates positions for symbols on the card based on their count.
        """
        positions = []
        center_x, center_y = size[0] // 2, size[1] // 2
        
        # Max radius for placement
        max_radius = min(center_x, center_y) - symbol_size - 10 
        
        if num_symbols <= 3:
            # Triangle
            radius = max_radius
            for i in range(num_symbols):
                angle = (2 * math.pi * i / num_symbols) + (math.pi / 2)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions.append((int(x), int(y)))
                
        elif num_symbols <= 4:
            # Square
            radius = max_radius
            for i in range(num_symbols):
                angle = (2 * math.pi * i / num_symbols) + (math.pi / 4)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions.append((int(x), int(y)))
                
        elif num_symbols <= 6:
            # One center, rest circle
            positions.append((center_x, center_y))
            radius = max_radius
            remaining = num_symbols - 1
            for i in range(remaining):
                angle = (2 * math.pi * i / remaining)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions.append((int(x), int(y)))
                
        else:
            # Two concentric circles
            inner_count = num_symbols // 3
            outer_count = num_symbols - inner_count
            
            # Inner circle
            inner_radius = max_radius * 0.35
            for i in range(inner_count):
                angle = (2 * math.pi * i / inner_count)
                x = center_x + inner_radius * math.cos(angle)
                y = center_y + inner_radius * math.sin(angle)
                positions.append((int(x), int(y)))
            
            # Outer circle
            outer_radius = max_radius
            for i in range(outer_count):
                angle = (2 * math.pi * i / outer_count)
                x = center_x + outer_radius * math.cos(angle)
                y = center_y + outer_radius * math.sin(angle)
                positions.append((int(x), int(y)))
        
        return positions

    @staticmethod
    def get_symbol_size(num_symbols):
        """
        Determines symbol size based on the number of symbols per card.
        """
        if num_symbols <= 4:
            return 180
        elif num_symbols <= 6:
            return 160
        elif num_symbols <= 8:
            return 140
        else:
            return 120

    @staticmethod
    def resize_image_with_aspect_ratio(image, max_size):
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height

        if original_width > original_height:
            new_width = max_size
            new_height = int(max_size / aspect_ratio)
        else:
            new_height = max_size
            new_width = int(max_size * aspect_ratio)

        return image.resize((new_width, new_height), resample=Resampling.LANCZOS)

    def create_cards(self, cards, symbols, enable_rotation=False, progress_callback=None):
        card_images = []
        card_size = (800, 800)
        total_cards_todo = len(cards)

        for i, card in enumerate(cards):
            img = Image.new('RGBA', card_size, color=(230, 227, 227, 255))
            draw = ImageDraw.Draw(img)
            
            center_x, center_y = card_size[0] // 2, card_size[1] // 2
            radius = min(center_x, center_y) - 20
            left_up = (center_x - radius, center_y - radius)
            right_down = (center_x + radius, center_y + radius)
            
            draw.ellipse([left_up, right_down], fill=(230, 227, 227, 255), outline=(135, 206, 250, 255), width=20)

            mask = Image.new('L', card_size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([left_up, right_down], fill=255)

            num_symbols = len(card)
            symbol_size = self.get_symbol_size(num_symbols)
            positions = self.get_positions(num_symbols, card_size, symbol_size)

            current_card_indices = list(card)
            random.shuffle(current_card_indices)

            for symbol_index, pos in zip(current_card_indices, positions):
                if symbol_index >= len(symbols):
                    continue

                symbol_img = symbols[symbol_index]
                symbol_img = self.resize_image_with_aspect_ratio(symbol_img, symbol_size)

                if symbol_img.mode != 'RGBA':
                    symbol_img = symbol_img.convert('RGBA')

                if enable_rotation:
                    random_angle = random.randint(-30, 30)
                    rotated_symbol_img = symbol_img.rotate(random_angle, expand=True)
                else:
                    rotated_symbol_img = symbol_img

                symbol_w, symbol_h = rotated_symbol_img.size
                pos_x = pos[0] - symbol_w // 2
                pos_y = pos[1] - symbol_h // 2
                img.paste(rotated_symbol_img, (pos_x, pos_y), rotated_symbol_img)

            img.putalpha(mask)
            filename = f'card_{i+1}.png'
            img.save(filename, format='PNG')
            card_images.append(filename)

            if progress_callback:
                progress_callback((i + 1) / total_cards_todo)

        return card_images

    @staticmethod
    def create_pdf(card_images, output_filename='dobble_cards.pdf'):
        pdf = FPDF('P', 'mm', 'A4')
        
        for i in range(0, len(card_images), 3):
            pdf.add_page()
            y_positions = [15, 105, 195]
            for j in range(3):
                if i + j < len(card_images):
                    img_path = card_images[i + j]
                    
                    try:
                        img = Image.open(img_path)
                        bg = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'RGBA':
                            bg.paste(img, mask=img.split()[3])
                        else:
                            bg.paste(img)
                        
                        temp_path = f'temp_{i + j}.png'
                        bg.save(temp_path, format='PNG')
                        
                        x_pos = (210 - 90) / 2
                        pdf.image(temp_path, x=x_pos, y=y_positions[j], w=90)
                        
                        os.remove(temp_path)
                    except Exception as e:
                        print(f"Error adding image to PDF: {e}")

        pdf.output(output_filename, 'F')
        return output_filename


class DobbleApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # Theme config
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        self.title("Custom Dobble Generator")
        self.geometry("800x650")
        
        self.generator = DobbleGenerator()
        self.folder_path = tk.StringVar()
        
        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = customtkinter.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        label_title = customtkinter.CTkLabel(main_frame, text="Dobble Generator", font=("Roboto", 24))
        label_title.pack(pady=20)

        # Folder Selection
        folder_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        folder_frame.pack(fill="x", pady=10)
        
        label_input = customtkinter.CTkLabel(folder_frame, text="Image Folder:")
        label_input.pack(anchor="w")
        
        entry_path = customtkinter.CTkEntry(folder_frame, textvariable=self.folder_path)
        entry_path.pack(fill="x", pady=5)
        
        btn_browse = customtkinter.CTkButton(folder_frame, text="Browse...", command=self.browse_folder)
        btn_browse.pack(pady=5)
        
        self.label_count = customtkinter.CTkLabel(main_frame, text="Images found: 0")
        self.label_count.pack(pady=5)

        # Options
        self.check_rotation = customtkinter.CTkCheckBox(main_frame, text="Random Rotation (±30°)")
        self.check_rotation.pack(pady=10)

        # Generate Button
        self.btn_generate = customtkinter.CTkButton(main_frame, text="Generate PDF", command=self.start_generation_thread)
        self.btn_generate.pack(pady=20)

        # Progress
        self.progressbar = customtkinter.CTkProgressBar(main_frame)
        self.progressbar.set(0)
        self.progressbar.pack(fill="x", padx=40, pady=10)

        # Info Table
        self.create_info_table(main_frame)

    def create_info_table(self, parent):
        table_frame = customtkinter.CTkFrame(parent)
        table_frame.pack(pady=20, fill="x")

        headers = ["Total Symbols\n(n^2 - n + 1)", "Symbols per Card (n)", "Cards Generated"]
        data = [
            [3, 2, 3],
            [7, 3, 7],
            [13, 4, 13],
            [21, 5, 21],
            [31, 6, 31],
            [43, 7, 43],
            [57, 8, 57],
        ]

        for col, header in enumerate(headers):
            lbl = customtkinter.CTkLabel(table_frame, text=header, font=("Arial", 12, "bold"))
            lbl.grid(row=0, column=col, padx=10, pady=5, sticky="ew")

        for r, row_data in enumerate(data, start=1):
            for c, value in enumerate(row_data):
                lbl = customtkinter.CTkLabel(table_frame, text=str(value), font=("Arial", 12))
                lbl.grid(row=r, column=c, padx=10, pady=5)
        
        table_frame.grid_columnconfigure((0, 1, 2), weight=1)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.count_images(folder_selected)

    def count_images(self, folder):
        count = 0
        valid_extensions = ('.png', '.jpg', '.jpeg')
        try:
            for filename in os.listdir(folder):
                if filename.lower().endswith(valid_extensions):
                    count += 1
            self.label_count.configure(text=f"Images found: {count}")
        except Exception as e:
            self.label_count.configure(text="Error reading folder")
            print(e)
            
    def start_generation_thread(self):
        # Run generation in a separate thread to keep UI responsive
        threading.Thread(target=self.run_generation, daemon=True).start()

    def run_generation(self):
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        self.btn_generate.configure(state="disabled")
        self.progressbar.set(0)

        try:
            images = self.generator.load_images(folder)
            k = len(images)
            if k < 3:
                messagebox.showerror("Error", "At least 3 images are required.")
                return

            symbols_per_card = self.generator.calculate_n(k) 
            total_symbols_needed = symbols_per_card**2 - symbols_per_card + 1
            
            if total_symbols_needed > k:
                 messagebox.showerror("Error", f"Not enough images. Required: {total_symbols_needed}")
                 return

            symbols_subset = images[:total_symbols_needed]
            cards = self.generator.generate_structure(symbols_per_card)
            
            rotation = (self.check_rotation.get() == 1)
            
            def update_progress(val):
                self.progressbar.set(val)
            
            card_images = self.generator.create_cards(
                cards, 
                symbols_subset, 
                enable_rotation=rotation, 
                progress_callback=update_progress
            )
            
            self.generator.create_pdf(card_images)
            
            messagebox.showinfo("Success", "PDF created successfully: dobble_cards.pdf")
            
        except Exception as e:
            messagebox.showerror("Critical Error", f"An error occurred:\n{e}")
            print(e)
        finally:
            self.btn_generate.configure(state="normal")


if __name__ == "__main__":
    app = DobbleApp()
    app.mainloop()
