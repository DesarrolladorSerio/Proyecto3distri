const validate = (schema) => {
  return (req, res, next) => {
    const { error } = schema.validate(req.body, { abortEarly: false });
    if (error) {
      const errorMessage = error.details.map((detail) => detail.message).join(', ');
      return res.status(400).json({
        error: {
          message: errorMessage,
          status: 400
        }
      });
    }
    next();
  };
};

module.exports = validate;
