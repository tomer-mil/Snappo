class ClotheObject:
    def __init__(self, clothe_id, category, color, size, image_path):
        self.clothe_id = clothe_id
        self.category = category
        self.color = color
        self.size = size
        self.image_path = image_path

    def __repr__(self):
        return f"ClotheObject(clothe_id={self.clothe_id}, category={self.category}, color={self.color}, size={self.size}, image_path={self.image_path})"

    def get_clothe_details(self):
        return {
            "clothe_id": self.clothe_id,
            "category": self.category,
            "color": self.color,
            "size": self.size,
            "image_path": self.image_path
        }

    def update_clothe_details(self, category=None, color=None, size=None, image_path=None):
        if category:
            self.category = category
        if color:
            self.color = color
        if size:
            self.size = size
        if image_path:
            self.image_path = image_path
