from django.conf import settings
from http import HTTPStatus
from langchain_openai import ChatOpenAI

from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, ToolMessage, ToolCall
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain

from .llm_tools import ExtractSQLQuery, ExtractVectorDBQuery, AddOrderProduct
from fastydli.customers.models import ConversationHistory
from fastydli.orders.models import ProductModel, OrderModel, OrderProductModel
from fastydli.desing_patterns.creations_patterns.singleton.vector_db_singleton import VectorDBSingleton


__author__ = 'Ricardo'
__version__ = '1.0'


class AIProviderSingleton():

    __client = None

    @classmethod
    def __get_connection(self):
        """
        This method create our client and give us a new thread
        """

        client = ChatOpenAI(
            model="gpt-4o",
            temperature=0.4,
            api_key=settings.OPENAI_API_KEY,
        ).bind_tools([ExtractSQLQuery, ExtractVectorDBQuery, AddOrderProduct])

        return client

    def __new__(cls, *args, **kwargs):

        if cls.__client == None:

            # making connection
            cls.__client = cls.__get_connection()

        return cls.__client

    @classmethod
    async def create_single_completion_message(cls, message):
        """
        This method creates a new completion message for single tasks

        :param message: the customer that we will use to create the completion message
        :return: a completion message
        """

        response = await cls.__client.ainvoke([HumanMessage(message)])

        return response

    @classmethod
    async def create_completion_message(cls, customer, order, user_message):
        """
        This method creates a new completion message

        :param customer: the customer that we will use to order
        :param order: the order that we will use to create add products
        :param user_message: the message that we will use to create the completion message
        :return: a completion message
        """

        message = {'data': {}, 'status_code': HTTPStatus.OK}

        from asgiref.sync import sync_to_async

        history = []

        # Convertimos el queryset en una lista de manera síncrona para evitar problemas al iterar
        conversation_messages = await sync_to_async(list)(ConversationHistory.objects.filter(customer=customer.id))

        for conversation_message in conversation_messages:
            if conversation_message.role == 'system':
                history.append(SystemMessage(conversation_message.message))
            elif conversation_message.role == 'user':
                history.append(HumanMessage(conversation_message.message))
            elif conversation_message.role == 'assistant':

                if conversation_message.type == 'message':
                    history.append(AIMessage(conversation_message.message))
                elif conversation_message.type == 'function':
                    history.append(AIMessage(content='', additional_kwargs={
                                   'tool_calls': conversation_message.tool_calls, 'refusal': None}))

            elif conversation_message.role == 'tool_call':
                history.append(ToolMessage(
                    content=conversation_message.message, tool_call_id=conversation_message.tool_call_id))

        for i in history:
            print(i.__repr__())
            print('--------------------')
        print()

        response_message = await cls.__client.ainvoke(history)

        print('#######################')

        if response_message.tool_calls:

            print(response_message.tool_calls)

            await sync_to_async(ConversationHistory.objects.create)(
                role='assistant', type='function', customer=customer, message='', tool_call_id=response_message.tool_calls[0]['id'], tool_calls=response_message.additional_kwargs['tool_calls']
            )

            history.append(AIMessage(content='', additional_kwargs={
                           'tool_calls': response_message.additional_kwargs['tool_calls'], 'refusal': None}))

            if response_message.tool_calls[0]['name'] == 'ExtractSQLQuery':

                db = SQLDatabase.from_uri("sqlite:///db.sqlite3")
                chain = create_sql_query_chain(cls.__client, db)
                query = await chain.ainvoke(
                    {"question": f"""Responde esta pregunta de usuario consultando solmente la tabla de products, en las consultas usa productos despues del from, solo debes retornar el sql sin el formato ```sql```, solo la cadena de consulta: {response_message.tool_calls[0]['args']['sql_query']}"""})
                response = db.run(query, fetch="cursor")
                res = f"""Datos obtenidos al consultar la base de datos: {
                    list(response.mappings())}, debo responder a la pregunta del usuario"""

                await sync_to_async(ConversationHistory.objects.create)(
                    role='tool_call', customer=customer, message=res, tool_call_id=response_message.tool_calls[0]['id'])

                history.append(ToolMessage(
                    content=res, tool_call_id=response_message.tool_calls[0]['id']))

                response_message = await cls.__client.ainvoke(history)

                await sync_to_async(ConversationHistory.objects.create)(
                    role='assistant', customer=customer, message=response_message.content
                )

                history.append(AIMessage(response_message.content))

            elif response_message.tool_calls[0]['name'] == 'ExtractVectorDBQuery':

                response = await AIProviderSingleton.create_single_completion_message(f'Debes de expandir esta pregunta, debe ser acorde teniendo en cuenta que se usará para hacer una búsqueda en una base de datos de vectores: {user_message}. Solo debes retornar la consulta expandida, nada mas')
                documents = await VectorDBSingleton.search_similarity_procedure(response.content)
                res = f"informacion encontrada: {documents}"

                await sync_to_async(ConversationHistory.objects.create)(
                    role='tool_call', customer=customer, message=res, tool_call_id=response_message.tool_calls[0]['id'])

                history.append(ToolMessage(
                    content=res, tool_call_id=response_message.tool_calls[0]['id']))

                response_message = await cls.__client.ainvoke(history)

                await sync_to_async(ConversationHistory.objects.create)(
                    role='assistant', customer=customer, message=response_message.content
                )

                history.append(AIMessage(response_message.content))

            elif response_message.tool_calls[0]['name'] == 'AddOrderProduct':

                product = response_message.tool_calls[0]['args']['product']
                quantity = response_message.tool_calls[0]['args']['quantity']

                product_gotten = await sync_to_async(ProductModel.objects.get)(name=product)

                await sync_to_async(OrderProductModel.objects.create)(order=order, product=product_gotten, quantity=quantity)

                res = 'El producto fue agregado correctamente'

                await sync_to_async(ConversationHistory.objects.create)(
                    role='tool_call', customer=customer, message=res, tool_call_id=response_message.tool_calls[0]['id'])

                history.append(ToolMessage(
                    content=res, tool_call_id=response_message.tool_calls[0]['id']))

                response_message = await cls.__client.ainvoke(history)

                await sync_to_async(ConversationHistory.objects.create)(
                    role='assistant', customer=customer, message=response_message.content
                )

                history.append(AIMessage(response_message.content))

        else:

            await sync_to_async(ConversationHistory.objects.create)(
                role='assistant', customer=customer, message=response_message.content
            )

            history.append(AIMessage(response_message.content))

        message['data'] = {'message': response_message.content}

        return message