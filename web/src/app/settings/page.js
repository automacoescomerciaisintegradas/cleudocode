"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = Settings;
const Layout_1 = __importDefault(require("@/components/layout/Layout"));
const SettingsPage_1 = __importDefault(require("@/components/settings/SettingsPage"));
function Settings() {
    return (<Layout_1.default>
      <SettingsPage_1.default />
    </Layout_1.default>);
}
