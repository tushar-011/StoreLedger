let cart = [];


const cartBody = document.getElementById("cartBody");

const cartData = document.getElementById("cartData");

const subtotalDisplay =
    document.getElementById("subtotalDisplay");

const totalDisplay =
    document.getElementById("totalDisplay");

const billingForm =
    document.getElementById("billingForm");

const productSearch =
    document.getElementById("productSearch");


document
    .querySelectorAll(".add-cart-button")
    .forEach(button => {

        button.addEventListener("click", function () {

            const productId =
                parseInt(this.dataset.id);

            const productName =
                this.dataset.name;

            const price =
                parseFloat(this.dataset.price);

            const stock =
                parseInt(this.dataset.stock);


            const existingProduct =
                cart.find(
                    item =>
                        item.product_id === productId
                );


            if (existingProduct) {

                if (
                    existingProduct.quantity >= stock
                ) {

                    alert(
                        "Cannot add more than available stock."
                    );

                    return;
                }

                existingProduct.quantity += 1;

            } else {

                cart.push({
                    product_id: productId,
                    product_name: productName,
                    price: price,
                    quantity: 1,
                    max_stock: stock
                });

            }


            renderCart();

        });

    });


function renderCart() {

    cartBody.innerHTML = "";


    if (cart.length === 0) {

        cartBody.innerHTML = `
            <tr>
                <td colspan="5"
                    class="empty-table">
                    No products added.
                </td>
            </tr>
        `;

        updateTotals();

        return;

    }


    cart.forEach(item => {

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                ${item.product_name}
            </td>

            <td>

                <input
                    type="number"
                    class="cart-quantity"
                    min="1"
                    max="${item.max_stock}"
                    value="${item.quantity}"
                    data-id="${item.product_id}"
                >

            </td>

            <td>
                ₹${item.price.toFixed(2)}
            </td>

            <td>
                ₹${(
                    item.price *
                    item.quantity
                ).toFixed(2)}
            </td>

            <td>

                <button
                    type="button"
                    class="remove-cart-button"
                    data-id="${item.product_id}"
                >
                    Remove
                </button>

            </td>
        `;


        cartBody.appendChild(row);

    });


    setupQuantityEvents();

    setupRemoveEvents();

    updateTotals();

}


function setupQuantityEvents() {

    document
        .querySelectorAll(".cart-quantity")
        .forEach(input => {

            input.addEventListener(
                "change",
                function () {

                    const productId =
                        parseInt(
                            this.dataset.id
                        );

                    let quantity =
                        parseInt(this.value);


                    const item =
                        cart.find(
                            product =>
                                product.product_id ===
                                productId
                        );


                    if (!item) {
                        return;
                    }


                    if (quantity < 1) {
                        quantity = 1;
                    }


                    if (
                        quantity >
                        item.max_stock
                    ) {

                        quantity =
                            item.max_stock;

                        alert(
                            "Quantity cannot exceed available stock."
                        );

                    }


                    item.quantity =
                        quantity;

                    this.value =
                        quantity;

                    renderCart();

                }
            );

        });

}


function setupRemoveEvents() {

    document
        .querySelectorAll(
            ".remove-cart-button"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                function () {

                    const productId =
                        parseInt(
                            this.dataset.id
                        );


                    cart =
                        cart.filter(
                            item =>
                                item.product_id !==
                                productId
                        );


                    renderCart();

                }
            );

        });

}


function updateTotals() {

    let subtotal = 0;


    cart.forEach(item => {

        subtotal +=
            item.price *
            item.quantity;

    });


    subtotalDisplay.textContent =
        `₹${subtotal.toFixed(2)}`;

    totalDisplay.textContent =
        `₹${subtotal.toFixed(2)}`;


    cartData.value =
        JSON.stringify(
            cart.map(item => ({
                product_id:
                    item.product_id,

                quantity:
                    item.quantity
            }))
        );

}


billingForm.addEventListener(
    "submit",
    function (event) {

        if (cart.length === 0) {

            event.preventDefault();

            alert(
                "Please add at least one product."
            );

        }

    }
);


productSearch.addEventListener(
    "input",
    function () {

        const searchValue =
            this.value
                .toLowerCase()
                .trim();


        document
            .querySelectorAll(
                "#productTable tbody tr"
            )
            .forEach(row => {

                const productName =
                    row
                        .children[0]
                        ?.textContent
                        .toLowerCase() || "";


                row.style.display =
                    productName.includes(
                        searchValue
                    )
                        ? ""
                        : "none";

            });

    }
);