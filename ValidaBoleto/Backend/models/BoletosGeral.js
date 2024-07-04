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
        nome: {
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
        email: {
          type: DataTypes.STRING,
          allowNull: true
        },
        cpfa: {
          type: DataTypes.STRING,
          allowNull: true
        },
        cpf: {
          type: DataTypes.STRING,
          allowNull: true
        },
        cpf2: {
          type: DataTypes.STRING,
          allowNull: true
        },
        pix: {
          type: DataTypes.STRING,
          allowNull: true
        },
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
