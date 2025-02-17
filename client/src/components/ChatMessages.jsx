import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";  // Enables tables, lists, and other markdown features
import { ShoppingCartIcon } from "@heroicons/react/24/outline";
import ProductSelection from "./ProductSelection";

export default function ChatMessages({ 
  messages, 
  pendingProduct, 
  selectedQuantity, 
  setSelectedQuantity, 
  handleAddToCart, 
  cart, 
  setCartOpen 
}) {
  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col flex-grow h-full items-center bg-gray-100">
      {/* Header */}
      <div className="w-full max-w-3xl bg-white shadow-md rounded-b-lg p-4 flex justify-between items-center fixed top-0 z-10">
        <span className="text-lg font-semibold text-gray-800">Farm2Bag Assistant</span>

        {/* Cart Button */}
        <button onClick={() => setCartOpen(true)} className="relative flex items-center text-gray-800">
          <ShoppingCartIcon className="w-7 h-7" />
          {cart.length > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full px-2">
              {cart.length}
            </span>
          )}
        </button>
      </div>

      {/* Chat Messages (Scrollable) */}
      <div className="flex-grow w-full max-w-3xl overflow-y-auto p-4 space-y-4 mt-16">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`p-4 rounded-lg shadow-md ${msg.sender === "user" ? "bg-green-500 text-white" : "bg-white text-gray-900"} max-w-2xl`}>
              {msg.sender === "bot" ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text || ""}</ReactMarkdown>
              ) : (
                msg.text
              )}
            </div>
          </div>
        ))}
        
        {/* Render inline product selection */}
        {pendingProduct && (
          <ProductSelection 
            product={pendingProduct} 
            selectedQuantity={selectedQuantity} 
            setSelectedQuantity={setSelectedQuantity} 
            handleAddToCart={handleAddToCart} 
          />
        )}

        {/* Always focus on the latest message */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
