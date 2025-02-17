export default function ChatInput({ input, setInput, handleSendMessage }) {
    const handleKeyPress = (e) => {
      if (e.key === "Enter") {
        handleSendMessage();
      }
    };
  
    return (
      <div className="p-4 bg-white shadow-md">
        <input
          type="text"
          className="w-full pl-4 pr-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none shadow-sm transition-all duration-200"
          placeholder="Enter your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
        />
      </div>
    );
  }
  