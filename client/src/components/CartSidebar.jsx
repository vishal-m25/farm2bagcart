import { XMarkIcon, TrashIcon } from "@heroicons/react/24/outline";

export default function CartSidebar({ cart, cartOpen, setCartOpen, removeFromCart }) {
  const totalPrice = cart.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2);

  return (
    <div className={`fixed top-0 right-0 w-80 h-full bg-white shadow-lg transform ${cartOpen ? "translate-x-0" : "translate-x-full"} transition-transform duration-300`}>
      <div className="flex justify-between items-center bg-green-600 text-white p-4">
        <h2 className="text-lg font-semibold">Shopping Cart</h2>
        <button onClick={() => setCartOpen(false)}>
          <XMarkIcon className="w-6 h-6" />
        </button>
      </div>
      <div className="p-4">
        {cart.map((item, index) => (
          <div key={index} className="flex justify-between p-2 border-b">
            <span>{item.quantity} x {item.name} - Rs. {item.price.toFixed(2)}</span>
            <button onClick={() => removeFromCart(index)}><TrashIcon className="w-5 h-5 text-red-500" /></button>
          </div>
        ))}
        <p className="text-lg font-semibold mt-4">Total: Rs. {totalPrice}</p>
      </div>
    </div>
  );
}
