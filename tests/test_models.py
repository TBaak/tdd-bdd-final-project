# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_a_product(self):
        """ It should Read a product from the database """
        product = ProductFactory()
        logging.info(product)
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        product_in_db = Product.find(product.id)
        # Assert that the product in the database has the correct values
        self.assertIsNotNone(product_in_db)
        self.assertEqual(product_in_db.name, product.name)
        self.assertEqual(product_in_db.description, product.description)
        self.assertEqual(product_in_db.price, product.price)
        self.assertEqual(product_in_db.available, product.available)
        self.assertEqual(product_in_db.category, product.category)

    def test_update_a_product(self):
        """ It should Update a product in the database """
        product = ProductFactory()
        logging.info(product)
        product.id = None
        product.create()
        logging.info(product)

        product.description = "Lorem ipsum"
        original_id = product.id
        product.update()
        # Assert that the ID stayed the same and the description was changed
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "Lorem ipsum")

        # Assert that there is still one product in the DB and that the values are correctly updated
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, product.id)
        self.assertEqual(products[0].description, "Lorem ipsum")

    def test_update_a_product_without_id(self):
        """ It should Update a product in the database without ID and raise an DataValidationError error """
        product = ProductFactory()
        logging.info(product)
        product.id = None
        logging.info(product)

        # Assert that updating a product without an ID raises a DataValidationError
        with self.assertRaises(DataValidationError):
            product.update()

        # Assert that there are still no products in the database
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_delete_a_product(self):
        """ It should Delete a product from the database """
        product = ProductFactory()
        logging.info(product)
        product.id = None
        product.create()
        logging.info(product)

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)

        # Assert that there is only one product in the DB
        products = Product.all()
        self.assertEqual(len(products), 1)

        product.delete()

        # Assert that there are no products in the DB
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """ It should List all products in the database """
        # Assert that there are no products in the DB
        products = Product.all()
        self.assertEqual(len(products), 0)

        for _ in range(0, 5):
            product = ProductFactory()
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)

        # Assert that there are now five products in the DB
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_a_product_by_name(self):
        """ It should find a product in the database by name """
        # Assert that there are no products in the DB
        all_products = Product.all()
        self.assertEqual(len(all_products), 0)

        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        # Assert that there are now five products in the DB
        all_products = Product.all()
        self.assertEqual(len(all_products), 5)

        name = products[0].name
        count_with_name = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        # Assert that the count of products with name is there same in the result as in the products list
        self.assertEqual(found.count(), count_with_name)
        # Assert that the name(s) of the found product are the same as the search
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_a_product_by_availability(self):
        """ It should find a product in the database by availability """
        # Assert that there are no products in the DB
        all_products = Product.all()
        self.assertEqual(len(all_products), 0)

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Assert that there are now ten products in the DB
        all_products = Product.all()
        self.assertEqual(len(all_products), 10)

        available = products[0].available
        count_with_availability = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        # Assert that the count of products with availability is there same in the result as in the products list
        self.assertEqual(found.count(), count_with_availability)
        # Assert that the availability of the found product are the same as the search
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_a_product_by_category(self):
        """ It should find a product in the database by category """
        # Assert that there are no products in the DB
        all_products = Product.all()
        self.assertEqual(len(all_products), 0)

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Assert that there are now ten products in the DB
        all_products = Product.all()
        self.assertEqual(len(all_products), 10)

        category = products[0].category
        count_with_category = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        # Assert that the count of products with category is there same in the result as in the products list
        self.assertEqual(found.count(), count_with_category)
        # Assert that the category of the found product are the same as the search
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_a_product_by_price(self):
        """ It should find a product in the database by price """
        # Assert that there are no products in the DB
        all_products = Product.all()
        self.assertEqual(len(all_products), 0)

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Assert that there are now ten products in the DB
        all_products = Product.all()
        self.assertEqual(len(all_products), 10)

        price = products[0].price
        count_with_price = len([product for product in products if product.price == price])
        found = Product.find_by_price(price)
        # Assert that the count of products with price is there same in the result as in the products list
        self.assertEqual(found.count(), count_with_price)
        # Assert that the price of the found product are the same as the search
        for product in found:
            self.assertEqual(product.price, price)

    def test_find_a_product_by_price_as_string(self):
        """ It should find a product in the database by price as string """
        # Assert that there are no products in the DB
        all_products = Product.all()
        self.assertEqual(len(all_products), 0)

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Assert that there are now ten products in the DB
        all_products = Product.all()
        self.assertEqual(len(all_products), 10)

        price = products[0].price
        count_with_price = len([product for product in products if product.price == price])
        found = Product.find_by_price(str(price))
        # Assert that the count of products with price is there same in the result as in the products list
        self.assertEqual(found.count(), count_with_price)
        # Assert that the price of the found product are the same as the search
        for product in found:
            self.assertEqual(product.price, price)

    def test_serialize_a_product(self):
        """ It should serialize a Product to a dictionary """

        product = ProductFactory()
        product.id = 1
        logging.info(product)
        # Serialize product
        serialized_product = product.serialize()
        logging.info(serialized_product)

        self.assertEqual(product.id, serialized_product["id"])
        self.assertEqual(product.name, serialized_product["name"])
        self.assertEqual(product.description, serialized_product["description"])
        self.assertEqual(str(product.price), serialized_product["price"])
        self.assertEqual(product.category.name, serialized_product["category"])

    def test_deserialize_a_product(self):
        """ It should deserialize a Product to a dictionary """

        product = ProductFactory()
        product.id = 1
        logging.info(product)
        # Serialize product
        serialized_product = product.serialize()
        logging.info(serialized_product)

        deserialized_product = product.deserialize(serialized_product)

        # Assert that alle the fields are the correct value
        self.assertEqual(deserialized_product.id, serialized_product["id"])
        self.assertEqual(deserialized_product.name, serialized_product["name"])
        self.assertEqual(deserialized_product.description, serialized_product["description"])
        self.assertEqual(str(deserialized_product.price), serialized_product["price"])
        self.assertEqual(deserialized_product.category.name, serialized_product["category"])

    def test_deserialize_a_product_with_invalid_availability(self):
        """ It shouldn't deserialize a Product to a dictionary with invalid availability """

        product = ProductFactory()
        product.id = 1
        logging.info(product)
        # Serialize product
        serialized_product = product.serialize()
        serialized_product['available'] = "Yes"
        logging.info(serialized_product)

        # Assert that updating a product without an ID raises a DataValidationError
        with self.assertRaises(DataValidationError) as dve:
            product.deserialize(serialized_product)
            logging.info(dve.msg)
            self.assertRegex(dve.msg, '*Invalid type for boolean*')

    def test_deserialize_a_product_with_invalid_attribute(self):
        """ It shouldn't deserialize a Product to a dictionary with invalid attribute """

        product = ProductFactory()
        product.id = 1
        logging.info(product)
        # Serialize product
        serialized_product = product.serialize()
        serialized_product['category'] = "Foo"
        logging.info(serialized_product)

        # Assert that updating a product without an ID raises a DataValidationError
        with self.assertRaises(DataValidationError) as dve:
            product.deserialize(serialized_product)
            logging.info(dve.msg)
            self.assertRegex(dve.msg, '*Invalid attribute*')

    def test_deserialize_a_product_with_invalid_key(self):
        """ It shouldn't deserialize a Product to a dictionary with invalid key """

        product = ProductFactory()
        product.id = 1
        logging.info(product)
        # Serialize product
        serialized_product = product.serialize()
        serialized_product.pop('name', None)
        logging.info(serialized_product)

        # Assert that updating a product without an ID raises a DataValidationError
        with self.assertRaises(DataValidationError) as dve:
            product.deserialize(serialized_product)
            logging.info(dve.msg)
            self.assertRegex(dve.msg, '*Invalid product: missing*')

    def test_deserialize_a_product_with_invalid_type(self):
        """ It shouldn't deserialize a Product to a dictionary with invalid type """

        product = ProductFactory()
        product.id = 1
        logging.info(product)
        # Serialize product
        serialized_product = product.serialize()
        serialized_product['category'] = {'foo': 1}
        logging.info(serialized_product)

        # Assert that updating a product without an ID raises a DataValidationError
        with self.assertRaises(DataValidationError) as dve:
            product.deserialize(serialized_product)
            logging.info(dve.msg)
            self.assertRegex(dve.msg, '*Invalid product: body of request contained bad or no data*')
