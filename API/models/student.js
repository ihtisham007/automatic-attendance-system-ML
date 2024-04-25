const mongoose = require('mongoose');

/**
 * @swagger
 * components:
 *  schemas:
 *     Student:
 *      type: object
 *     required:
 *     - title
 *     - author
 *
 */

const studentSchema = new mongoose.Schema({
    id: {
        type: Number,
        required: [true, 'A Student must have an id'],
        unique: true
    },
    name: {
        type: String,
        required: [true, 'A Student must have a Name']
    },
    department: {
        type: String,
        require: [true, 'A Student must have a Department']
    },
    createdAt: {
        type: Date,
        default: Date.now()
    },
    __v: {
        type: Number,
        select: false
    }
});

const Student = mongoose.model('Student', studentSchema);

module.exports = Student;