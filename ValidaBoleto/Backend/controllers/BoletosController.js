const axios = require ('axios');
const { validate } = require('gerador-validador-cpf');

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
console.log(resposta)
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




  async consultaBoleto (req,res)
  {
    const {mat,cpf} = req.body;
    const cpf_procurado=cpf;

    function validarCPF(cpf) {
      // Remove caracteres não numéricos do CPF
      cpf = cpf.replace(/\D/g, '');
  
      // Verifica se o CPF é válido usando a função da biblioteca
      return validate(cpf);
  }

    function hasLetters(str) {
      // Expressão regular para verificar se a string contém qualquer letra
      const regex = /[a-zA-Z]/;
    
      // Testa a string contra a expressão regular
      return regex.test(str);
    }

  console.log("m",mat,cpf)

    try {
                      
      if ((!mat)) return res.status(200).json({varRet : "Matrícula não enviado."});
      if ((!cpf)) return res.status(200).json({varRet : "CPF não enviado."});

      if (!validarCPF(cpf)) return res.status(200).json({varRet : "CPF inválido."});
      if (hasLetters(mat))   return res.status(200).json({varRet : "Matrícula deve ser só numeros."});
      if (mat.length != 9 )  return res.status(200).json({varRet : "Numero da Matrícula inválido."});


        const resposta = await BoletosGeral.findAll({
          where: {
            mat,
            // [Sequelize.Op.or]: [
            //   { cpf:cpf },
            //   { cpfa:cpf },
            //   { cpf2:cpf }
            // ],
            // token: {
            //   [Sequelize.Op.ne]: null
            // }
          },
          // order: [['data_gerado', 'DESC']], // Ordena por data_registro em ordem decrescente
          // limit: 1 // Limita o resultado para apenas um registro
        });
      
        if ((resposta.length > 0)) {

          console.log(resposta[0].dataValues)
          const { cpf, cpfa, cpf2,token } = resposta[0].dataValues
          console.log(cpf_procurado,cpf,cpfa,cpf2)

          if (!(cpf === cpf_procurado || cpfa === cpf_procurado || cpf2 === cpf_procurado)) 
             return res.status(200).json({ varRet: `O CPF ${cpf_procurado} não esta associado com a matrícula ${mat}.`});


          if (!(token === null )) {
                return res.status(200).json({ resultado:true, varRet: "Segue o link do seu boleto: https://boletos.santamonicarede.com.br/"+resposta[0].dataValues.token});
                // return res.status(200).json({ varRet: "Segue o link do seu boleto: http://192.168.1.214:3353/"+resposta[0].dataValues.token});
          }
          else{
            return res.status(200).json({resultado:false, varRet : "Sr.Responsável, não foi possível o processamento da Solicitação. O PDF não foi gerado para este aluno pela unidade. Favor entrar em contato com a Supervisão."});
          }
        }
        else {
          return res.status(200).json({resultado:false, varRet : `Sr. Responsável, não consta registro para a matricula ${mat}. Por gentileza, verifique se está fornecendo os dados corretamente.` });
        }

    }catch(error)
    { 
        console.log(error)
        return res.status(400).json({ erros: ['Erro inesperado'] });
      }

    }



}