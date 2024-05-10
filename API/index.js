const express = require('express');
const bodyParser = require('body-parser')
const path = require('path')

const apiRoutes = require('./routes/apiRoutes');
const globalErrorHandler = require('./controllers/errorController');
const studentController = require('./controllers/studentController');


const application = express();

application.use(express.json());

application.use(bodyParser.urlencoded())

application.use(bodyParser.urlencoded({
  extended: true
}));

application.use('/public', express.static(path.join(__dirname ,'static')));
application.set('view engine', 'ejs');

application.get('/', (req,res) =>{
    res.render('index')
})

application.get('/student', async(req,res)=>{
    const students = await studentController.getALLStudents();
    res.render('student', {data : students})
});

application.get('/attendance', async(req,res)=>{
    const data  = await studentController.getAttendance(req, res)
    console.log(data)
    res.render('attendance', {data : data})
})


application.use('/api/v1/student', apiRoutes);
application.use(globalErrorHandler);

module.exports = application;