import requests

API_URL = 'http://127.0.0.1:5000'



if __name__ == '__main__':

    resource = ''
    endpoint = '{}/{}'.format(API_URL, resource)

    response = requests.get(endpoint)
    if not response.ok:
        print('system not working')
    else:
        print(response.json())

    resource = 'flights'
    endpoint = '{}/{}'.format(API_URL, resource)

    flightsRes = requests.get(endpoint)
    if flightsRes.ok:
        if(len(flightsRes.json())==0):
            print("no flight yet")
            print("you can run celery to see how automatic processing work")
            print("use this command celery -A CS403_Assign1_bkoseoglu.celery worker --loglevel=info -P eventlet")
            resource = 'flights/add'
            endpoint = '{}/{}'.format(API_URL,resource)
            addedFlight = requests.get(endpoint)
            print(addedFlight.json(),'addedFlight')
            if addedFlight.ok:
                flightNum = addedFlight.json().get("f_uid")
                print(flightNum)
                resource = 'flight/' + flightNum
                endPoint = '{}/{}'.format(API_URL, resource)
                print(endPoint,'endP')
                flightDetails = requests.get(endPoint)
                print(flightDetails.json(),'flightDetails')
                if flightDetails.ok:
                    if(len(flightDetails.json().get('not_avaliable_seats'))!=50):
                        resource = 'flight/' + flightNum + '/buy'
                        endpoint = '{}/{}'.format(API_URL, resource)
                        buyFlight = requests.get(endpoint)
                        if buyFlight.ok:
                            resource = 'ticket/' + str(buyFlight.json().get("ticket_uid"))
                            endpoint = '{}/{}'.format(API_URL, resource)
                            ticketDetails = requests.get(endpoint)
                            if ticketDetails.ok:
                                print('my ticket is: ' + str(ticketDetails.json()))
                            else:
                                print('connection lost')
                        else:
                            print(buyFlight.json())
                    else:
                        print(flightDetails.json())
                else:
                    print('connection lost')
            else:
                print('connecton lost')
        else:
            flights = list(flightsRes.json().keys())
            flightNum = flights[0]
            resource = 'flight/' + flightNum
            print(flightNum)
            endPoint = '{}/{}'.format(API_URL, resource)
            print(endPoint, 'endP')
            flightDetails = requests.get(endPoint)
            print(flightDetails.json())
            if flightDetails.ok:
                if (len(flightDetails.json().get('not_avaliable_seats')) != 50):
                    resource = 'flight/' + flightNum + '/buy'
                    endpoint = '{}/{}'.format(API_URL, resource)
                    buyFlight = requests.get(endpoint)
                    if buyFlight.ok:
                        resource = 'ticket/' + str(response.json().get("ticket"))
                        endpoint = '{}/{}'.format(API_URL, resource)
                        TicketDetails = requests.get(endpoint)
                        if TicketDetails.ok:
                            print('my ticket is: ' + str(TicketDetails.json()))
                        else:
                            print('connection lost')
                    else:
                        print(buyFlight.json())
                else:
                    print(flightDetails.json())
            else:
                print('connection lost')
    else:
        print('connection lost')



