const route = require('express').Router();

const studentController = require('../controllers/studentController');


//without any parameter it will call
route
    .route('/')
    .get(studentController.getStudents)
    .post(studentController.saveStudent);


//with id parameter it will call
route
    .route('/getAllStudentAttendance')
    .get(studentController.getAllStudentAttendance)

route
    .route('/:id/saveattendance')
    .post(studentController.saveAttendance)
//    .delete(bookController.deleteBook);

module.exports = route;