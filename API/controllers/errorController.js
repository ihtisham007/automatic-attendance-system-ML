/**
 * @swagger
 * tags:
 * name: ErrorController
 * description: Error handling and error messages for production and development environment
 *              All Methods sendErrorDev(err, res), sendErrorProd(err, res), handleCastErrorDB(err), handleDuplicateFieldsDB(err), handleValidationErrorDB(err)
 *              It will also handle all errors from the application or it will convert mongodb error to meaningful error messages
 *               
 */

const AppError = require('./../utils/appError');

const handleCastErrorDB = (err) => {

   return new AppError(`Invalid id`, 400);
}

const handleDuplicateFieldsDB = (err) => {
    return new AppError(`Duplicate field value entered ${err['keyValue']['id']}`, 400);
}

const handleValidationErrorDB = (err) => {
    const errors = Object.values(err.errors).map(el => el.path + ': ' + el.value + ' ' + el.kind + ',');
    return new AppError(`Invalid input data please check ${errors}`, 400);
}

const sendErrorDev = (err, res) => {

    res.status(err.statusCode).json({
        status: err.status,
        error: err,
        message: err.message,
        stack: err.stack,

    })
}


const sendErrorProd = (err, res) => {
    //Operational, trusted error: send message to client
    if(err.isOperational){
        res.status(err.statusCode).json({
            status: err.status,
            message: err.message,
        })
    // Programming or other unknown error: don't leak error details
    }else{
        //1) Log error
        console.error(`ERROR 💥: ${err}`);
        //2) Send generic message
        res.status(500).json({
            status: 'Error',
            message: 'Something went very wrong',
        })
    }

}


module.exports = (err, req, res, next) => {
    err.statusCode = err.statusCode || 500;
    err.status = err.status || 'Error';

    if(process.env.NODE_ENV === 'development'){
       sendErrorDev(err, res);

    }else if(process.env.NODE_ENV === 'production'){
        let error = {...err};
        if(error.statusCode === 404) error =  handleCastErrorDB(error);
        if(error.code === 11000)  error =  handleDuplicateFieldsDB(error);
        if(error._message === 'User validation failed') error =  handleValidationErrorDB(error);
        sendErrorProd(error, res);
   
    }

}