"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = DashboardPage;
const Layout_1 = __importDefault(require("@/components/layout/Layout"));
const Dashboard_1 = __importDefault(require("@/components/dashboard/Dashboard"));
function DashboardPage() {
    return (<Layout_1.default>
      <Dashboard_1.default />
    </Layout_1.default>);
}
