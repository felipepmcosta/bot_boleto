const express = require("express");

const routes = express.Router();


routes.use(function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*"); // update to match the domain you will make the request from
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

const BoletoController = require("../controllers/BoletosController");

routes.post("/consultaMat", BoletoController.consultaBoleto);

routes.use("/:token", BoletoController.validaBoleto);



  // return res.status(200).json("Servidor OK");
  

module.exports = routes;
