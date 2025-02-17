import Cart from "./components/CartSidebar.jsx";
import Chatbot from "./Chatbot";
import Lottie from "lottie-react";
import backgroundAnimation from "./assets/background.json";

export default function App() {
  return (
    <div className="relative flex flex-col h-screen bg-gray-100">
      {/* Background Animation */}
      <Lottie 
        animationData={backgroundAnimation} 
        loop={true} 
        autoplay={true}
        className="absolute inset-0 w-full h-full object-cover z-0" 
      />



      {/* Main Content */}
      <div className="relative z-10 flex-grow flex flex-col">
        <Chatbot />
      </div>
    </div>
  );
}
