const express = require("express");
const routes = require("./routes");

const cors = require("cors");

require("../database");

const app = express();
app.use(cors());

app.use("/pdf", express.static(__dirname));
// /home/marcos/Documentos/mol/Fullstack/BackEnd/controllers/teste.pdf

console.log(__dirname);

app.use(express.json());
app.use(routes);

app.listen(3353);
