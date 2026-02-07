"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = Chat;
const Layout_1 = __importDefault(require("@/components/layout/Layout"));
const ChatInterface_1 = __importDefault(require("@/components/chat/ChatInterface"));
function Chat() {
    return (<Layout_1.default>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Chat with Cleudocode</h1>
          <p className="text-gray-600 dark:text-gray-400">Have a conversation with your AI assistant</p>
        </div>
        <ChatInterface_1.default />
      </div>
    </Layout_1.default>);
}
