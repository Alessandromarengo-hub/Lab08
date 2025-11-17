from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        risultati = []
        for impianto in self._impianti:
            consumi = impianto.get_consumi()
            consumi_mese = []
            for c in consumi:
                if c.data.month == mese:
                    consumi_mese.append(c.kwh)

            media = sum(consumi_mese)/len(consumi_mese)
            risultati.append((impianto.nome, media))

        return risultati

        # TODO

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        if giorno == 8:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = [i.id for i in sequenza_parziale]
            return

        if self.__costo_ottimo != -1 and costo_corrente >= self.__costo_ottimo:
            return

        indice_consumo = giorno - 1
        for impianto in self._impianti:
            costo_giornaliero = consumi_settimana[impianto.id][indice_consumo]
            penalita_spostamento = 0

            if ultimo_impianto is not None and impianto != ultimo_impianto:
                penalita_spostamento = 5

            nuovo_costo_accumulato = costo_corrente + costo_giornaliero + penalita_spostamento
            sequenza_parziale.append(impianto)

            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,
                impianto,  # Il nuovo ultimo impianto è l'impianto appena scelto
                nuovo_costo_accumulato,
                consumi_settimana
            )

            sequenza_parziale.pop()
        # TODO

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        impianto_per_consumo = {}
        for impianto in self._impianti:
            consumi = impianto.get_consumi()
            # Filtra solo i consumi del mese e dei primi 7 giorni
            consumi_settimana = [
                c.kwh for c in consumi
                if c.data.month == mese and 1 <= c.data.day <= 7
            ]
            impianto_per_consumo[impianto.id] = consumi_settimana
        return impianto_per_consumo
        # TODO

