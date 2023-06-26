if (localStorage.getItem("cart") == null) {
  var cart = {};
} else {
  cart = JSON.parse(localStorage.getItem("cart"));
  updateCart(cart);
}

// If the add to cart button is clicked, add/increment the item
function AddToCart(idstr) {}
$(".divpr").on("click", "button.cart", function () {
  var idstr = this.id.toString();
  if (cart[idstr] != undefined) {
    qty = cart[idstr].quantity + 1;
    cart[idstr] = { quantity: qty, ...cart[idstr] };
  } else {
    qty = 1;
    name = document.getElementById("name" + idstr).innerHTML;
    price = document.getElementById("price" + idstr).innerHTML;
    description = document.getElementById("desc" + idstr).innerHTML;
    image = document.getElementById("img" + idstr).getAttribute("src");
    cart[idstr] = {
      name: name,
      description: description,
      quantity: qty,
      price: parseInt(price),
      src: image,
    };
  }
  // console.log("cart: ",cart)
  updateCart(cart);
});

function updateCart(cart) {
  var sum = 0;
  console.log("My cart: ", cart);
  for (var item in cart) {
    console.log(
      "cart item: ",
      cart[item].quantity,
      " type: ",
      typeof cart[item]
    );
    sum += cart[item].quantity;
    document.getElementById("div" + item).innerHTML =
      "<button id='minus" +
      item +
      "' class='btn btn-primary minus'>-</button> <span id='val" +
      item +
      "''>" +
      cart[item].quantity +
      "</span> <button id='plus" +
      item +
      "' class='btn btn-primary plus'> + </button>";
  }
  localStorage.setItem("cart", JSON.stringify(cart));
  document.getElementById("cart").innerHTML = sum;
  console.log("total: ", sum);
  //  updatePopover(cart);
  updateSideCart(cart);
}

function updateSideCart(cart) {
  let i = 1;
  document.getElementById("cart-item").innerHTML = "";
  let total = 0;
  for (var item in cart) {
    total += cart[item].quantity * cart[item].price;
    document.getElementById("cart-item").innerHTML +=
      "<div class='mycard row'><div class='card-body col-md-7'><h5 class='card-title'>" +
      cart[item].name +
      "</h5><p class='card-text'>" +
      cart[item].description +
      "</p><p class='card-quantity'>" +
      cart[item].quantity +
      " X " +
      "₹" +
      cart[item].price +
      "</p></div><div class='col-md-5  mt-3'><img src=" +
      cart[item].src +
      " height='150px' width='100px'/></div></div><br/>";
  }
  document.getElementById("cart-price").innerHTML =
    "₹" + total.toLocaleString();
}

function clearCart() {
  cart = JSON.parse(localStorage.getItem("cart"));
  for (var item in cart) {
    document.getElementById("div" + item).innerHTML =
      '<button id="' +
      item +
      '" class="btn btn-primary cart">Add To Cart</button>';
  }
  localStorage.clear();
  cart = {};
  updateCart(cart);
}

// If plus or minus button is clicked, change the cart as well as the display value
$(".divpr").on("click", "button.minus", function () {
  a = this.id.slice(7);
  cart["pr" + a].quantity = cart["pr" + a].quantity - 1;
  cart["pr" + a].quantity = Math.max(0, cart["pr" + a].quantity);
  document.getElementById("valpr" + a).innerHTML = cart["pr" + a];
  updateCart(cart);
});
$(".divpr").on("click", "button.plus", function () {
  a = this.id.slice(6);
  cart["pr" + a].quantity = cart["pr" + a].quantity + 1;
  document.getElementById("valpr" + a).innerHTML = cart["pr" + a].quantity;
  updateCart(cart);
});
