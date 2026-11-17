function guardarComentarioInseguro(req) {
  const feedback = {
    // ruleid: feedback-userid-no-confiar-cliente
    UserId: req.body.UserId,
    comment: req.body.comment,
    rating: req.body.rating
  };
  return feedback;
}

function guardarComentarioInseguroAlternativo(request) {
  const feedback = {
    // ruleid: feedback-userid-no-confiar-cliente
    UserId: request.body.userId,
    comment: request.body.comment
  };
  return feedback;
}

function guardarComentarioSeguro(req) {
  const feedback = {
    // ok: feedback-userid-no-confiar-cliente
    UserId: req.user.id,
    comment: req.body.comment,
    rating: req.body.rating
  };
  return feedback;
}

function guardarComentarioSeguroConSesion(request) {
  const feedback = {
    // ok: feedback-userid-no-confiar-cliente
    UserId: request.session.userId,
    comment: request.body.comment
  };
  return feedback;
}