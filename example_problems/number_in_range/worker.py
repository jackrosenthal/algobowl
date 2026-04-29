import algops.app
import asgi
import problem
import workers

app = algops.app.ProblemSupportApplication(
    input_type=problem.Input,
    output_type=problem.Output,
    rank_sort=algops.app.RANK_SORT_MINIMIZATION,
    score_decimal_places=0,
    statements=[
        algops.app.Statement.pdf("/statement.pdf"),
        algops.app.Statement.markdown("/statement.md"),
    ],
)


class Default(workers.WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(app, request, self.env)
