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
        """It should Read a product"""
        # Create a Product object using the ProductFactory
        product = ProductFactory()

        # Add a log message displaying the product for debugging errors
        app.logger.info("Initiate Reading Test for %s", product.name)

        # Set the ID of the product object to None and then create the product.
        product.id = None
        product.create()

        # Assert that the product ID is not None
        self.assertIsNotNone(product.id)

        # Assert that the product ID is not None
        db_product = Product.find_by_name(product.name)[0]

        # Assert that the product ID is not None
        self.assertEqual(db_product.id, product.id)
        self.assertEqual(db_product.description, product.description)
        self.assertEqual(db_product.available, product.available)
        self.assertEqual(db_product.price, product.price)
        self.assertEqual(db_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a product"""
        # Create a Product object using the ProductFactory
        product = ProductFactory()

        # Add a log message displaying the product for debugging errors
        app.logger.info("Initiate Updating Test for %s", product.serialize())

        # Set the ID of the product object to None and create the product.
        product.id = None
        product.create()

        # Log the product object again after it has been created to verify that the product was
        # created with the desired properties.
        app.logger.info("Created %s", product.name)

        # Update the description property of the product object.
        product.description = "foo"

        # Assert that that the id and description properties of the product object have been updated correctly.
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "foo")

        # Fetch all products from the database to verify that after updating the product, there is
        # only one product in the system.
        products = Product.all()
        self.assertEqual(len(products), 1)

        # Assert that the fetched product has the original id but updated description.
        self.assertEqual(products[0].id, product.id)
        self.assertEqual(products[0].description, "foo")

    def test_update_a_product_with_none_id(self):
        """It should raise an error when Updating a product with a None ID"""
        # Create a Product object using the ProductFactory
        product = ProductFactory()

        # Add a log message displaying the product for debugging errors
        app.logger.info("Initiate Updating Test for %s", product.name)

        # Set the ID of the product object to None and create the product.
        product.id = None
        product.create()

        # Log the product object again after it has been created to verify that the product was
        # created with the desired properties.
        app.logger.info("Created %s", product.name)

        # Update the ID to None.
        product.id = None

        # Assert that the update function raises an error
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a product"""
        # Create a Product object using the ProductFactory and save it to the database.
        product = ProductFactory()
        product.create()

        # Assert that after creating a product and saving it to the database, there is only one product in the system.
        products = Product.all()
        self.assertEqual(len(products), 1)

        # Remove the product from the database.
        product.delete()

        # Assert if the product has been successfully deleted from the database.
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should List all products in the Database"""
        # Retrieve all products from the database and assign them to the products variable.
        products = Product.all()

        # Assert there are no products in the database at the beginning of the test case.
        self.assertEqual(len(products), 0)

        # Create five products and save them to the database.
        for _ in range(5):
            product = ProductFactory()
            product.create()

        # Fetching all products from the database again and assert the count is 5
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_a_product_by_name(self):
        """It should Find a Product by its name in the Database"""
        # Create a batch of 5 Product objects using the ProductFactory and save them to the database.
        product_list = []
        for _ in range(5):
            product = ProductFactory()
            product_list.append(product)
            product.create()

        # Retrieve the name of the first product in the products list
        first_name = product_list[0].name

        # Count the number of occurrences of the product name in the list
        occurrences = len([p for p in product_list if p.name == first_name])

        # Retrieve products from the database that have the specified name.
        db_products = Product.find_by_name(first_name)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(db_products.count(), occurrences)

        # Assert that each product’s name matches the expected name.
        for db_p in db_products:
            self.assertEqual(db_p.name, first_name)

    def test_find_a_product_by_availability(self):
        """It should Find a Product by its availability in the Database"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database.
        product_list = []
        for _ in range(10):
            product = ProductFactory()
            product_list.append(product)
            product.create()

        # Retrieve the availability of the first product in the products list
        first_available = product_list[0].available

        # Count the number of occurrences of the product availability in the list
        occurrences = len([p for p in product_list if p.available == first_available])

        # Retrieve products from the database that have the specified availability.
        db_products = Product.find_by_availability(first_available)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(db_products.count(), occurrences)

        # Assert that each product’s name matches the expected name.
        for db_p in db_products:
            self.assertEqual(db_p.available, first_available)

    def test_find_a_product_by_category(self):
        """It should Find a Product by its category in the Database"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database.
        product_list = []
        for _ in range(10):
            product = ProductFactory()
            product_list.append(product)
            product.create()

        # Retrieve the category of the first product in the products list
        first_category = product_list[0].category

        # Count the number of occurrences of the product that have the same category in the list.
        occurrences = len([p for p in product_list if p.category == first_category])

        # Retrieve products from the database that have the specified category.
        db_products = Product.find_by_category(first_category)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(db_products.count(), occurrences)

        # Assert that each product's category matches the expected category.
        for db_p in db_products:
            self.assertEqual(db_p.category, first_category)
