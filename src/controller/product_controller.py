import os

from flask import Flask
from werkzeug.utils import secure_filename

from src.database.sql.products import ProductsORM, CategoryORM
from src.database.models.products import Product, Category
from src.controller import Controllers, error_handler
from src.utils import static_folder


class ProductController(Controllers):
    def __init__(self):
        super().__init__()

    def init_app(self, app: Flask):
        super().init_app(app=app)
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}

    import os

    @staticmethod
    async def create_category_link(category_name: str, extension: str) -> str | None:
        """
        Create a category image link based on the category name and extension.
        :param category_name: The name of the category
        :param extension: The file extension of the image
        :return: The category image link
        """
        category_name = category_name.lower().strip()
        extension = extension.lower().strip()

        # Sanitize extension
        if "." in extension:
            extension = extension.split(".")[1]
        extension = extension.lower().strip()

        # Obtain the path to the static folder
        static_folder_path = static_folder()

        # Construct the directory path for the category
        category_dir = os.path.join("images", "inventory", category_name)
        os.makedirs(os.path.join(static_folder(), category_dir), exist_ok=True)
        # Create the category directory if it doesn't exist
        # os.makedirs(f"{static_folder()}/{category_dir}", exist_ok=True)

        # Construct the image link
        return os.path.join(category_dir, f"{category_name}.{extension}")

        # Return the image link
        # return image_link.replace("\\", "/")  # Replace backslashes for Windows compatibility

    @staticmethod
    async def create_product_link(category_name: str, product_name: str, extension: str) -> str | None:
        """

        :param category_name:
        :param product_name:
        :param extension:
        :return:
        """
        category_name = category_name.lower().strip()
        product_name = product_name.lower().strip()
        if "." in extension:
            extension = extension.split(".")[1]
        extension = extension.lower().strip()

        if category_name and product_name and extension:
            return os.path.join(f"{static_folder()}images/inventory/{category_name}/{product_name}.{extension}")
        else:
            return None

    async def get_product(self, product_id: str) -> Product | None:
        """

        :param product_id:
        :return:
        """
        with self.get_session() as session:
            product_orm = session.query(ProductsORM).filter_by(product_id=product_id).first()
            if isinstance(product_orm, ProductsORM):
                return Product(**product_orm.to_dict())
            return None

    async def get_products(self) -> list[Product]:
        """

        :return:
        """
        with self.get_session() as session:
            products_list_orm = session.query(ProductsORM).all()
            return [Product(**product_orm.to_dict()) for product_orm in products_list_orm
                    if isinstance(product_orm, ProductsORM)]

    async def get_categories(self) -> list[Category]:
        """

        :return:
        """
        with self.get_session() as session:
            category_list_orm = session.query(CategoryORM).all()
            return [Category(**category_orm.to_dict()) for category_orm in category_list_orm
                    if isinstance(category_orm, CategoryORM)]

    async def add_category(self, category_detail: Category) -> Category:
        """

        :return:
        """
        with self.get_session() as session:
            name = category_detail.name.lower().strip()
            category_orm = session.query(CategoryORM).filter_by(name=name).first()

            if isinstance(category_orm, CategoryORM):
                category_orm.name = category_detail.name.lower().strip()
                category_orm.description = category_detail.description.lower().strip()
                category_orm.products_list = category_detail.products_list
                category_orm.img_link = category_detail.img_link

            else:
                category_orm = CategoryORM(**category_detail.dict())
                session.add(category_orm)

            session.commit()

            return category_detail

    async def save_category_image(self, category_name: str, image) -> str:
        """
            will return image link
        :return:
        """
        filename = secure_filename(image.filename)
        ext_list = filename.split(".")
        extension = ext_list[-1]
        extension = extension.lower().strip()

        if extension not in self.allowed_extensions:
            return None

        destination_image_path = await self.create_category_link(category_name=category_name, extension=extension)
        print(f"Static Folder : {static_folder()}")
        print(f"Image Path : {destination_image_path}")
        save_file = f"{static_folder()}/{destination_image_path}"
        print(f"Save File Destination: {save_file}")
        image.save(save_file)
        return destination_image_path

    async def get_category_details(self, category_name: str) -> Category | None:
        """

        :param category_name:
        :return:
        """
        category_name.lower().strip()
        with self.get_session() as session:
            category_detail_orm = session.query(CategoryORM).filter_by(name=category_name.casefold()).first()
            if isinstance(category_detail_orm, CategoryORM):
                return Category(**category_detail_orm.to_dict())

            return None

    async def get_category_products(self, category_id: str) -> list[Product]:
        """

        :param category_id:
        :return:
        """
        with self.get_session() as session:
            products_orm_list = session.query(ProductsORM).filter_by(category_id=category_id).all()

            return [Product(**product_orm.to_dict()) for product_orm in products_orm_list
                    if isinstance(product_orm, ProductsORM)]

    async def add_category_product(self, category_id: str, product: Product):
        """

        :param category_id:
        :param product:
        :return:
        """
        with self.get_session() as session:
            name = product.name.lower().strip()
            product_orm = session.query(ProductsORM).filter_by(name=name).first()
            if isinstance(product_orm, ProductsORM):
                product_orm.name = name
                product_orm.category_id = category_id
                product_orm.product_id = product.product_id

                if product.description:
                    product_orm.description = product.description
                if product.sale_price:
                    product_orm.sale_price = product.sale_price
                if product.cost_price:
                    product_orm.cost_price = product.cost_price
                if product.img_link:
                    product_orm.img_link = product.img_link
                if product.inventory_entries:
                    product_orm.inventory_entries = product.inventory_entries
            else:
                product_orm = ProductsORM(**product.dict())
                session.add(product_orm)

            session.commit()

            return product

    async def add_product_image(self, category_id: str, product_name: str, image) -> str:
        """

        :param category_id:
        :param product_name:
        :param image:
        :return:
        """
        filename = secure_filename(image.filename)
        ext_list = filename.split(".")
        ext = ext_list[-1]
        ext = ext.lower().strip()
        filename = f"{product_name.lower().strip()}.{ext}"
        print(f"filename : {filename}")
        with self.get_session() as session:
            category_detail: CategoryORM = session.query(CategoryORM).filter_by(category_id=category_id).first()

            img_link = category_detail.img_link
            category_location = img_link
            category_location = os.path.dirname(img_link)
            static_folder()

            save_location = os.path.join(static_folder(), category_location, filename)
            print(f"Save Location : {save_location}")
            image.save(save_location)
            return os.path.join(category_location, filename)


