const route = require('express').Router();
const path = require('path');

const studentController = require('../controllers/studentController');


// Route for handling student data
route
    .route('/')
    .get(studentController.getStudents)
    .post(studentController.saveStudent);


route
    .route('/:id/getstudentname')
    .get(studentController.getStudentNameById)

// Route for handling student attendance
route
    .route('/getAllStudentAttendance')
    .get(studentController.getAllStudentAttendance);

// Route for saving student attendance
route
    .route('/:id/saveattendance')
    .post(studentController.saveAttendance);

module.exports = route;
