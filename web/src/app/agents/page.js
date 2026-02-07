"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = Agents;
const Layout_1 = __importDefault(require("@/components/layout/Layout"));
const AgentsPage_1 = __importDefault(require("@/components/agents/AgentsPage"));
function Agents() {
    return (<Layout_1.default>
      <AgentsPage_1.default />
    </Layout_1.default>);
}
