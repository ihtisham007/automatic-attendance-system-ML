const mongoose = require('mongoose');

const attendanceSchema = new mongoose.Schema({
    studentId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Student', // Reference to the Student model
        required: true
    },
    status: {
        type: Number,
        enum: [0, 1], // 0 for absent, 1 for present
        required: true
    },
    dateTime: {
        type: Date,
        default: Date.now
    }
});

const Attendance = mongoose.model('Attendance', attendanceSchema);

module.exports = Attendance;
