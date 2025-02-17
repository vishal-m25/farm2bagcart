export default function ProductSelection({ product, selectedQuantity, setSelectedQuantity, handleAddToCart }) {
  return (
    <div className="flex justify-start">
      <div className="p-3 rounded-lg shadow-md max-w-xs bg-gray-200 text-gray-800">
        <p className="font-semibold">{product.name}</p>
        <p>Price: Rs. {product.price}</p>

        {/* Display Measuring Base Value if Available */}
        {product.measuring_base_value && (
          <p className="text-sm text-gray-600">Unit: {product.measuring_base_value}</p>
        )}

        <label className="block my-2">
          Quantity:
          <input
            type="number"
            className="border w-full mt-1 p-2 rounded"
            value={selectedQuantity}
            min="1"
            onChange={(e) => setSelectedQuantity(Number(e.target.value))}
          />
        </label>

        <button
          className="w-full bg-green-500 text-white px-4 py-2 rounded mt-2"
          onClick={() => handleAddToCart(product, selectedQuantity)}
        >
          Add to Cart
        </button>
      </div>
    </div>
  );
}
