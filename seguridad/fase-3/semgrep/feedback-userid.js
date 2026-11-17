
const FeedbackModel = {
  create: async (data) => data
}

async function feedbackInseguro(req) {
  // ruleid: feedback-userid-no-confiar-cliente
  await FeedbackModel.create({
    comment: req.body.comment,
    UserId: req.body.UserId,
    rating: 3
  })
}

async function feedbackInseguroRequest(request) {
  // ruleid: feedback-userid-no-confiar-cliente
  await FeedbackModel.create({
    comment: request.body.comment,
    UserId: request.body.UserId,
    rating: 4
  })
}

async function feedbackSeguro(req) {
  const authenticatedUserId = req.user.id

  // ok: feedback-userid-no-confiar-cliente
  await FeedbackModel.create({
    comment: req.body.comment,
    UserId: authenticatedUserId,
    rating: 3
  })
}
