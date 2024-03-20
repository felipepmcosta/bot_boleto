const Sequelize = require("sequelize");
const dbConfig = require("../config/database");

// const User = require("../models/User");
// const Address = require("../models/Address");
// const Tech = require("../models/Tech");
// const Login = require("../models/Login");

const BoletosGeral = require("../models/BoletosGeral");

const connection = new Sequelize(dbConfig);


// User.init(connection);
// Address.init(connection);
// Tech.init(connection);
// Login.init(connection);


BoletosGeral.init(connection);

// User.associate(connection.models);
// Address.associate(connection.models);
// Tech.associate(connection.models);

module.expores = connection;
