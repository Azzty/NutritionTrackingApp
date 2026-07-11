import flet as ft
import services.livsmedelsverket_client as livsmedelsverket_client

db_client = livsmedelsverket_client.LivsmedelsverketClient()

def main(page: ft.Page):
    page.title = "Livsmedelsverket DB search"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER

    results_view = ft.Column()

    def update_results(e):
        query = search_input.value
        results = db_client.search_foods_by_name(query)
        results_view.controls = [ft.Text(value=r.name) for r in results]

    search_input = ft.TextField(value="", text_align=ft.TextAlign.RIGHT, width=400, hint_text="Sök", on_change=update_results)

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls = [
                search_input
            ]
        ),
        results_view
    )

ft.run(main)