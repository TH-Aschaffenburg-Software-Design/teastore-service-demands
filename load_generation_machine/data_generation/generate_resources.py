"""
Create a json file containing an array of 100 session blobs. (One for each available user)
Each of the session blobs has items in the shopping cart.

Impl Note:
The products are added to the shopping carts in natural order, 2 items in each shopping cart.
"""
import json
import os
from requests import get, post

from utils import get_service_ip


def main():

    GEN_DIR = "generated"
    os.makedirs(GEN_DIR, exist_ok=True)
    products_file = f"{GEN_DIR}/products.json"
    sessionblob_file = f"{GEN_DIR}/sessionBlobs.json"

    auth_ip = get_service_ip("auth")
    persistence_ip = get_service_ip("persistence")

    product_response = get(f"http://{persistence_ip}:8080/tools.descartes.teastore.persistence/rest/products")
    products: list = product_response.json()

    with open(products_file, "w") as file:
        json.dump(products, file, indent=4)

    product_count = len(products)

    blobs = []
    for i in range(100):
        login_response = post(f"http://{auth_ip}:8080/tools.descartes.teastore.auth/rest/useractions/login?name=user{i}&password=password", json={})
        blob = login_response.json()
        for k in range(2):
            index = (i * 2 + k) % product_count
            pid = products[index]["id"]
            cart_response = post(f"http://{auth_ip}:8080/tools.descartes.teastore.auth/rest/cart/add/{pid}", json=blob)
            blob = cart_response.json()
        blobs.append(blob)

    with open(sessionblob_file, "w") as file:
        json.dump(blobs, file, indent=4)

if __name__ == "__main__":
    main()
