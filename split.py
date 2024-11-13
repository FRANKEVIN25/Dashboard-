def split_file(entrada, salida, porcion=524288):
    input_file = open(entrada, encoding="utf-8")        # Codificación utf-8 para evitar errores

    counter = 0         # Contador de líneas
    part = 0            # Contador de partes

    output_file = open(salida+str(part)+".csv", "a", encoding="utf-8")

    for line in input_file:                             # Barrido de líneas
        if counter % porcion == 0 and counter != 0:     # Porciones
            print("Escrito el archivo: "+salida+str(part))
            output_file.close()
            part += 1
            output_file = open(salida+str(part)+".csv", "a", encoding="utf-8")
        output_file.write(line)                         # Escribir líneas
        counter += 1
    print("Archivos divididos exitosamente: "+str(part+1))    # Mensaje final

split_file("2023-Gasto-Mensual.csv", "2023-Gasto-Mensual-Parte")
