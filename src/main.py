import flet as ft

from repositories.utils.DB import DB
from repositories.debt.DebtRepository import DebtRepository
from repositories.person.PersonRepository import PersonRepository
from repositories.payment.PaymentRepository import PaymentRepository
from repositories.transaction.TransactionRepository import TransactionRepository

from services.debt.DebtService import DebtService
from services.person.PersonService import PersonService
from services.payment.PaymentService import PaymentService
from services.transaction.TransactionService import TransactionService

from controllers.debt.DebtController import DebtController
from controllers.person.PersonController import PersonController
from controllers.payment.PaymentController import PaymentController
from controllers.transaction.TransactionController import TransactionController

from views.debts import debts_view
from views.people import people_view
from views.payments import payments_view
from views.transactions import transactions_view
from views.welcome import welcome_view, appbar_app, get_user_name


async def main(page: ft.Page):
    page.title = "FinTrack"

    db = DB()

    person_repo = PersonRepository(db)
    person_service = PersonService(person_repo)
    person_controller = PersonController(person_service, page)

    transaction_repo = TransactionRepository(db)
    transaction_service = TransactionService(transaction_repo)
    transaction_controller = TransactionController(transaction_service, page)

    payment_repo = PaymentRepository(db)
    payment_service = PaymentService(payment_repo)
    payment_controller = PaymentController(payment_service, page)

    debt_repo = DebtRepository(db, payment_repo)
    debt_service = DebtService(debt_repo)
    debt_controller = DebtController(debt_service, transaction_service, page)

    status = {"user_name": await get_user_name(page)}

    def main_view() -> ft.View:
        return ft.View(
            route="/",
            controls=[
                appbar_app("Inicio", status["user_name"]),
                ft.Container(
                    padding=20,
                    content=ft.Column(
                        [
                            ft.FilledButton(
                                "Personas",
                                icon=ft.Icons.PEOPLE,
                                on_click=lambda e: page.navigate("/people"),
                            ),
                            ft.FilledButton(
                                "Transacciones",
                                icon=ft.Icons.SWAP_VERT,
                                on_click=lambda e: page.navigate("/transactions"),
                            ),
                            ft.FilledButton(
                                "Deudas",
                                icon=ft.Icons.MONEY_OFF,
                                on_click=lambda e: page.go("/debts"),
                            ),
                            ft.FilledButton(
                                "Pagos",
                                icon=ft.Icons.PAYMENTS,
                                on_click=lambda e: page.go("/payments"),
                            ),
                        ],
                        spacing=10,
                    ),
                ),
            ],
        )

    async def on_continue(name:str):
        status["user_name"] = name
        route_change()

    def route_change(e: ft.RouteChangeEvent = None):
        page.views.clear()

        if not status["user_name"]:
            page.views.append(welcome_view(page, on_continue))

        elif page.route == "/people":
            page.views.append(people_view(page, person_controller, status["user_name"]))
        
        elif page.route == "/transactions":
            page.views.append(transactions_view(page, transaction_controller, status["user_name"]))
        
        elif page.route == "/debts":
            page.views.append(debts_view(page, debt_controller, person_controller, status["user_name"]))
        
        elif page.route == "/payments":
            page.views.append(payments_view(page,payment_controller,debt_controller,person_controller,status["user_name"],))
        
        else:
            page.views.append(main_view())
        
        page.update()

    page.on_route_change = route_change
    route_change()

ft.run(main)