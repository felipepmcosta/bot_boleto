const { Model, DataTypes } = require('sequelize');

class BoletosGeral extends Model {
  static init(sequelize) {
    return super.init(
      {
        id: {
          type: DataTypes.INTEGER,
          primaryKey: true,
          autoIncrement: true
        },
        mat: {
          type: DataTypes.STRING
        },
        cot: {
          type: DataTypes.STRING
        },
        boleto: {
          type: DataTypes.BLOB('long')
        },
        digitavel: {
          type: DataTypes.TEXT
        },
        token: {
          type: DataTypes.STRING
        },
        envio: {
          type: DataTypes.DATE
        },
        geracao: {
          type: DataTypes.DATE
        },
        
        nome: {
          type: DataTypes.STRING
        }
      },
      {
        sequelize,
        // modelName: 'BoletosGeral',
        tableName: 'boletos_geral', // Se a tabela estiver em um esquema específico
        timestamps: false // Se você não quiser os campos de timestamps
      }
    );
  }
}

module.exports = BoletosGeral;
