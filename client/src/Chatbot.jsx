import { useState, useRef, useEffect } from "react";
import ChatHistory from "./components/ChatHistory";
import ChatMessages from "./components/ChatMessages";
import ChatInput from "./components/ChatInput";
import CartSidebar from "./components/CartSidebar";

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [chats, setChats] = useState([]);
  const [cart, setCart] = useState([]);
  const [cartOpen, setCartOpen] = useState(false);
  const [pendingProduct, setPendingProduct] = useState(null);
  const [selectedQuantity, setSelectedQuantity] = useState(1);
  const messagesEndRef = useRef(null);

  const handleSendMessage = async (messageText = input) => {
    if (messageText.trim() === "") return;

    const newMessages = [...messages, { sender: "user", text: messageText }];
    setMessages(newMessages);
    setInput("");

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: messageText }),
      });

      const data = await response.json();
      setMessages([...newMessages, { sender: "bot", text: data.response }]);

      // If a product is suggested, set it for inline selection
      if (data.product) {
        setPendingProduct(data.product);
        setSelectedQuantity(1);
      }
    } catch (error) {
      console.error("Error fetching bot response:", error);
      setMessages([...newMessages, { sender: "bot", text: "**Sorry, I couldn't process your request.**" }]);
    }
  };

  const fetchCart = async () => {
    try {
      const response = await fetch("http://localhost:5000/view_cart"); // Make sure this endpoint exists in Flask
      const data = await response.json();
      setCart(data.cart || []);  // Update cart state
    } catch (error) {
      console.error("Error fetching cart:", error);
    }
  };
  

  const handleAddToCart = async (product, quantity) => {
    try {
      const response = await fetch("http://localhost:5000/add_to_cart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: product.name, price: product.price, quantity }),
      });
  
      const data = await response.json();
  
      // Update cart state directly instead of fetching
      setCart((prevCart) => [...prevCart, { ...product, quantity }]);
  
      // Add confirmation message in chat
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: `✅ *${quantity} x ${product.name}* added to cart.` }
      ]);
      setPendingProduct(null);
    } catch (error) {
      console.error("Error adding to cart:", error);
    }
  };
  
   



  const removeFromCart = (index) => setCart(cart.filter((_, i) => i !== index));

  return (
    <div className="flex h-screen bg-gray-100">
      <ChatHistory chats={chats} startNewChat={() => setMessages([])} loadChat={() => {}} />
      <div className="flex flex-col flex-grow">
      <ChatMessages 
        messages={messages} 
        pendingProduct={pendingProduct} 
        selectedQuantity={selectedQuantity} 
        setSelectedQuantity={setSelectedQuantity} 
        handleAddToCart={handleAddToCart} 
        messagesEndRef={messagesEndRef} 
        cart={cart} 
        setCartOpen={setCartOpen} 
      />
      <ChatInput input={input} setInput={setInput} handleSendMessage={handleSendMessage} />
      </div>
      <CartSidebar cart={cart} cartOpen={cartOpen} setCartOpen={setCartOpen} removeFromCart={removeFromCart} />
    </div>
  );
}
