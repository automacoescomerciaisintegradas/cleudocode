"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = App;
const AuthContext_1 = require("@/contexts/AuthContext");
require("@/styles/globals.css");
function App({ Component, pageProps }) {
    return (<AuthContext_1.AuthProvider>
      <Component {...pageProps}/>
    </AuthContext_1.AuthProvider>);
}
