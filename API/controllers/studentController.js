const student = require('./../models/student');
const attendance = require('./../models/attendance');
const APIFeatures = require('../utils/apiFeatures');
const catchAsync = require('./../utils/catchAsync');
const AppError = require('./../utils/appError');

/**
 * @swagger
 * tags:
 * name: StudentController
 * description: Student management and retrieval
 *              All Methods get(getStudents), post(saveStudent), patch(updateStudent), delete(deleteStudent)
 *
 * */

const getStudents = catchAsync(async (req, res, stat,next) => {

    const features = new APIFeatures(student.find(), req.query)
        .filter()
        .sort()
        .limitFields()
        .paginate();
    const students = await features.query;

    res
        .status(200)
        .json({
            status: 'success',
            data: students
        });
});

const getALLStudents = async () => {

    const allStudents = await student.find();

    return allStudents;
};

const saveStudent = catchAsync(async (req, res, next) => {

    const newStudent = req.body;
    const savedStudent = await student.create(newStudent);
    res
        .status(201)
        .json({
            status: 'success',
            data: savedStudent
        });

});

const saveAttendance = async (req, res, stat = 1) => {

     // Get the student ID from the request
        const studentId = req.params.id; // Assuming the student ID is in the URL parameter
        console.log('asd');
        // Find the student by ID
        const foundStudent = await student.findOne({id: studentId})

        if (!foundStudent) {
            return res.status(404).json({
                status: 'fail',
                message: 'Student not found !!!'
            });
        };

        // Create a new attendance record
        const newAttendance = {
            studentId: foundStudent._id,
            status: 1, // Assuming the status is in the request body
        };

        // Save the attendance record
        const savedAttendance = await attendance.create(newAttendance);


        res.status(201).json({
            status: 'success',
            data: savedAttendance,
            studentBio: foundStudent
        });
};

const getAllStudentAttendance = catchAsync(async (req, res, next) => {

        // Find all students
        const allStudents = await student.find();

        // Create an array to store student attendance data
        const studentAttendanceData = [];

        // Iterate through each student
        for (const student of allStudents) {
            // Find attendance records for the student within a date range (e.g., last 7 days)
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - 7); // Adjust the date range as needed

            const attendanceRecords = await attendance.find({
                studentId: student._id,
                dateTime: { $gte: startDate } // Filter by date range
            })
            .select('status dateTime') // Select only status and dateTime fields
            .sort('-dateTime'); // Sort by dateTime in descending order

            // Add student information and attendance records to the array
            studentAttendanceData.push({
                student: {
                    id: student._id,
                    name: student.name,
                    department: student.department
                },
                attendance: attendanceRecords
            });
        }

        res.status(200).json({
            status: 'success',
            data: studentAttendanceData
        });
});

// Example usage:
// GET /students/attendance
// Returns attendance records for all students within the date range

const getAttendance = async() => {
     // Find all students
        const allStudents = await student.find();

        // Create an array to store student attendance data
        const studentAttendanceData = [];

        // Iterate through each student
        for (const student of allStudents) {
            // Find attendance records for the student within a date range (e.g., last 7 days)
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - 7); // Adjust the date range as needed

            const attendanceRecords = await attendance.find({
                studentId: student._id,
                dateTime: { $gte: startDate } // Filter by date range
            })
            .select('status dateTime') // Select only status and dateTime fields
            .sort('-dateTime'); // Sort by dateTime in descending order

            // Add student information and attendance records to the array
            studentAttendanceData.push({
                student: {
                    id: student.id,
                    name: student.name,
                    department: student.department
                },
                attendance: attendanceRecords
            });
        }

     return studentAttendanceData

}

module.exports = {
    getStudents,
    getALLStudents,
    saveStudent,
    getAllStudentAttendance,
    saveAttendance,
    getAttendance,
};