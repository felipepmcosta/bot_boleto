// require("dotenv/config");

// module.exports = {
//   dialect: "postgres",
//   username: process.env.DB_USER,
//   password: process.env.DB_PASS,
//   database: process.env.DB_NAME,
//   host: process.env.DB_HOST,
//   port: process.env.DB_PORT,

//   define: {
//     timestamp: true,
//     underscored: true,
//     underscoredAll: true,
//   },
// };

require("dotenv/config");

module.exports = {
  dialect: "postgres",
  username: process.env.DB_USER ,
  password: process.env.DB_PASS ,
  database: process.env.DB_NAME ,
  host: process.env.DB_HOST ,
  port: process.env.DB_PORT ,
  define: {
    timestamp: true,
    underscored: true,
    underscoredAll: true,
  },
};
