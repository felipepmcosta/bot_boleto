const axios = require ('axios');

const { QueryTypes } = require("sequelize");
const fs = require('fs');

const Sequelize = require("sequelize");
const dbConfig = require("../config/database");
const connection = new Sequelize(dbConfig);

const BoletosGeral = require('../models/BoletosGeral');


module.exports = {
  
   
  async validaBoleto (req,res)

  {
  console.log(req.params.token)
    try {
                      
      if (!req.params.token){
        return res.status(400).json({erros : ['Token não enviado']});
      }
  
      console.log("teste")
      const resposta = await BoletosGeral.findAll({where : { token : req.params.token}});

      if (!resposta || resposta.length === 0) {
        return res.status(400).json({ erros: ['Registro Token não existe'] });
      }
    
      // Assume-se que o campo 'boleto' é onde está armazenado o PDF em formato bytea
      const boletoBytea = resposta[0].boleto;
    
      if (!boletoBytea) {
        return res.status(400).json({ erros: ['Boleto não encontrado'] });
      }
    
      // Convertendo bytea para Buffer
      const buffer = Buffer.from(boletoBytea, 'binary');
    
      // Configurando os headers da resposta para indicar que é um PDF
      res.setHeader('Content-Type', 'application/pdf');
      res.setHeader('Content-Disposition', 'inline; filename="boleto.pdf"');

      // Enviando o PDF como parte da resposta
      res.send(buffer);

      console.log('Boleto enviado com sucesso.');
      } catch (error) {
        console.error('Erro ao enviar o boleto:', error);
        return res.status(500).json({ erros: ['Erro ao enviar o boleto'] });
      }
  },



          // const resultado = await cb_credito.create({ payment_type,
          //   customer_id,
          //   order_id,
          //   payment_id,
          //   amount,
          //   status,
          //   number_installments,
          //   acquirer_transaction_id,
          //   authorization_timestamp,
          //   brand,
          //   terminal_nsu,
          //   authorization_code,
          //   combined_id,
          //   description_detail,
          //   error_code, }, { returning: true });

          //   return res.status(200).json(resultado); 



}