-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: sweetland_by_anny
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `detalle_pedidos`
--

DROP TABLE IF EXISTS `detalle_pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_pedidos` (
  `id_detalle` int NOT NULL AUTO_INCREMENT,
  `pedido_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `pedido_id` (`pedido_id`),
  KEY `producto_id` (`producto_id`),
  CONSTRAINT `detalle_pedidos_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id_pedido`) ON DELETE CASCADE,
  CONSTRAINT `detalle_pedidos_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_pedidos`
--

LOCK TABLES `detalle_pedidos` WRITE;
/*!40000 ALTER TABLE `detalle_pedidos` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalle_pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empaques`
--

DROP TABLE IF EXISTS `empaques`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empaques` (
  `id_empaque` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id_empaque`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empaques`
--

LOCK TABLES `empaques` WRITE;
/*!40000 ALTER TABLE `empaques` DISABLE KEYS */;
INSERT INTO `empaques` VALUES (1,'Bolsa transparente x1','Bolsa individual para 1 unidad',111.00),(2,'Bolsa transparente x2','Bolsa para 2 unidades',150.00),(3,'Bolsa transparente x4','Bolsa para 4 unidades',200.00),(4,'Bolsa transparente x6','Bolsa para 6 unidades',250.00),(5,'Bolsa transparente x12','Bolsa para 12 unidades',400.00),(6,'Bolsa transparente x16','Bolsa para 16 unidades',2160.00),(7,'Bolsa transparente x20','Bolsa para 20 unidades',6000.00),(8,'Bolsita individual','Bolsita pequeña por unidad',300.00),(9,'Bolsa plástica','Bolsa plástica genérica',300.00),(10,'Caja individual x1','Caja para 1 unidad (tortas/cupcake)',1500.00),(11,'Caja x4 unidades','Caja para 4 unidades',9054.00),(12,'Caja x6 unidades','Caja para 6 unidades',10032.00),(13,'Caja grande','Caja para tortas grandes',10000.00),(14,'Caja surtida x6','Caja surtida para 6 brownies',30096.00),(15,'Sticker x1','Sticker individual',111.00),(16,'Sticker x4','Paquete de 4 stickers',333.00),(17,'Sticker x6','Paquete de 6 stickers',666.00),(18,'Sticker x9','Paquete de 9 stickers',999.00),(19,'Sticker x12','Paquete de 12 stickers',1332.00),(20,'Sticker x16','Paquete de 16 stickers',3996.00),(21,'Capacillo #1 x1','Capacillo individual pequeño',50.00),(22,'Capacillo x2','Paquete de 2 capacillos',180.00),(23,'Capacillo x4','Paquete de 4 capacillos',180.00),(24,'Capacillo x6','Paquete de 6 capacillos',180.00),(25,'Capacillo x9','Paquete de 9 capacillos',180.00),(26,'Capacillo x12','Paquete de 12 capacillos',180.00),(27,'Capacillo x16','Paquete de 16 capacillos',432.00),(28,'Capacillo x36','Paquete de 36 capacillos',432.00),(29,'Capacillo x100','Caja de 100 capacillos',1200.00),(30,'Blonda','Blonda decorativa para tortas',400.00),(31,'Blonda MDF','Base de MDF para tortas grandes',15000.00),(32,'Domo 1/8','Domo plástico para torta 1/8',12000.00),(33,'Domo individual','Domo plástico para torta pequeña',3000.00),(34,'Taza veneciana 8 onz','Taza para cheesecake frío',5100.00),(35,'Vaso plástico','Vaso desechable',250.00),(36,'Cuchara desechable','Cuchara plástica',100.00),(37,'Molde de aluminio','Molde desechable para tiramisú',1000.00),(38,'Empaque sándwich','Empaque individual para sándwich',500.00),(39,'Topper','Topper decorativo para torta',15000.00),(40,'Soporte para torta','Soporte metálico/plástico',2300.00),(41,'Topper anillos','Topper especial diseño anillos',22000.00);
/*!40000 ALTER TABLE `empaques` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ingredientes`
--

DROP TABLE IF EXISTS `ingredientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredientes` (
  `id_ingrediente` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `unidad` varchar(20) NOT NULL,
  `cantidad` decimal(10,2) NOT NULL,
  `costo_unitario` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_ingrediente`)
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredientes`
--

LOCK TABLES `ingredientes` WRITE;
/*!40000 ALTER TABLE `ingredientes` DISABLE KEYS */;
INSERT INTO `ingredientes` VALUES (46,'Harina pastelera','gr',0.00,4.00),(47,'Harina común','gr',0.00,3.20),(48,'Azúcar blanca','gr',0.00,4.40),(49,'Azúcar morena','gr',0.00,4.29),(50,'Azúcar glass','gr',0.00,14.00),(51,'Margarina','gr',0.00,12.00),(52,'Mantequilla','gr',0.00,58.80),(53,'Aceite vegetal','ml',0.00,8.33),(54,'Leche líquida','ml',0.00,4.22),(55,'Leche entera','ml',0.00,3.60),(56,'Leche en polvo','gr',0.00,18.00),(57,'Leche condensada','ml',0.00,14.97),(58,'Crema de leche','ml',0.00,11.50),(59,'Chantilly','ml',0.00,21.00),(60,'Queso crema','gr',0.00,24.00),(61,'Queso crema Colanta','gr',0.00,16.50),(62,'Queso blanco','gr',0.00,27.77),(63,'Huevos','und',0.00,500.00),(64,'Esencia de vainilla','ml',0.00,32.00),(65,'Vainilla en gr','gr',0.00,16.00),(66,'Estevia líquida','ml',0.00,73.33),(67,'Cocoa','gr',0.00,48.00),(68,'Ph (polvo hornear)','gr',0.00,16.00),(69,'Polvo de hornear','gr',0.00,16.00),(70,'Bicarbonato','gr',0.00,5.00),(71,'Fécula de maíz','gr',0.00,14.00),(72,'Maicena','gr',0.00,6.00),(73,'Leche en polvo premium','gr',0.00,22.00),(74,'Sal','gr',0.00,2.49),(75,'Merengue en polvo','gr',0.00,0.00),(76,'Chocolate Negro Cordillera','gr',0.00,44.00),(77,'Chocolate Luker','gr',0.00,44.44),(78,'Chocolate blanco','gr',0.00,40.00),(79,'Trozos de chocolate','gr',0.00,40.00),(80,'Lluvia de colores','gr',0.00,36.00),(81,'M&M\'s','gr',0.00,72.00),(82,'Colorante rojo','gr',0.00,2500.00),(83,'Papel comestible','und',0.00,10000.00),(84,'Papel oro','und',0.00,2000.00),(85,'Crema de avellanas','gr',0.00,31.29),(86,'Avellana','gr',0.00,28.29),(87,'Galletas Oreo','gr',0.00,44.00),(88,'Galletas Muuu','gr',0.00,26.66),(89,'Arequipe','gr',0.00,13.00),(90,'Fresas','gr',0.00,14.00),(91,'Mora','gr',0.00,20.00),(92,'Cereza','gr',0.00,70.00),(93,'Maracuyá','ml',0.00,24.00),(94,'Bocadillo','gr',0.00,12.66),(95,'Auyama','gr',0.00,6.66),(96,'Vinagre','ml',0.00,2.85),(97,'Café','gr',0.00,102.94),(98,'Gelatina sin sabor','gr',0.00,73.33),(99,'Yogurt griego','ml',0.00,22.12),(100,'Quipitos','und',0.00,800.00),(101,'Pan tajado','und',0.00,257.00),(102,'Queso tajado','und',0.00,538.00),(103,'Jamón','und',0.00,521.32),(104,'Gaseosa','ml',0.00,2.59);
/*!40000 ALTER TABLE `ingredientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagos`
--

DROP TABLE IF EXISTS `pagos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagos` (
  `id_pago` int NOT NULL AUTO_INCREMENT,
  `id_pedido` int NOT NULL,
  `metodo` enum('efectivo','tarjeta','transferencia','nequi','daviplata') NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `fecha_pago` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `estado` enum('pendiente','confirmado','fallido') DEFAULT 'pendiente',
  PRIMARY KEY (`id_pago`),
  KEY `id_pedido` (`id_pedido`),
  CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagos`
--

LOCK TABLES `pagos` WRITE;
/*!40000 ALTER TABLE `pagos` DISABLE KEYS */;
/*!40000 ALTER TABLE `pagos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos` (
  `id_pedido` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `fecha_pedido` datetime DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `direccion` varchar(255) NOT NULL,
  `telefono` varchar(50) NOT NULL,
  `estado` varchar(50) DEFAULT 'pendiente',
  PRIMARY KEY (`id_pedido`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos`
--

LOCK TABLES `pedidos` WRITE;
/*!40000 ALTER TABLE `pedidos` DISABLE KEYS */;
/*!40000 ALTER TABLE `pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `categoria` enum('tortas','postres','detalles') NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `utilidad_porcentaje` decimal(5,2) DEFAULT '40.00' COMMENT 'Porcentaje de utilidad deseado',
  `pax` int DEFAULT '1' COMMENT 'Unidades que rinde la receta',
  `costo_produccion` decimal(10,2) DEFAULT '0.00' COMMENT 'Costo total de producción',
  `precio_sugerido` decimal(10,2) DEFAULT '0.00' COMMENT 'Precio sugerido de venta',
  PRIMARY KEY (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=616 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (595,'Torta Rosa','tortas','Torta decorada con rosas en crema, ideal para celebraciones femeninas.',70000.00,'torta rosa.jpg',48.00,10,24370.60,9528.90),(596,'Torta Personalizada','tortas','Diseño exclusivo hecho a mano según tu temática favorita.',75000.00,'tortapersonalizada.jpg',50.00,1,10746.00,29762.29),(597,'Torta Hello Kitty','tortas','Perfecta para cumpleaños infantiles. Encanto y ternura en cada capa.',73000.00,'tortapersonalizadahellokitty.jpg',40.00,1,0.00,0.00),(598,'Torta Happy Birthday','tortas','Decoración colorida con mensaje especial de cumpleaños.',72000.00,'tortahappybirthday.jpg',40.00,1,0.00,0.00),(599,'Torta Sonic','tortas','Torta temática de Sonic, ideal para fans del personaje veloz.',74000.00,'tortasonic.jpg',40.00,1,0.00,0.00),(600,'Torta de Auyama','tortas','Deliciosa torta tradicional con bocadillo y queso, sabor casero.',69000.00,'tortaauyama.jpg',40.00,1,0.00,0.00),(601,'Galletas de Chocolate','postres','Suaves y crocantes, con chips de chocolate.',3000.00,'galletaschocolate.jpg',40.00,1,0.00,0.00),(602,'Galletas Personalizadas','postres','Diseños únicos para cada ocasión especial.',3500.00,'galletaspersonalizadas.jpg',40.00,1,0.00,0.00),(603,'Galletas Rellenas','postres','Rellenas de chocolate o masmello, ideales para regalar.',4000.00,'galletasrellenas.jpg',40.00,1,0.00,0.00),(604,'Cupcakes Decorados','postres','Coloridos y con sabor a vainilla o chocolate.',5000.00,'cupcakes.jpg',40.00,1,0.00,0.00),(605,'Cupcakes Temáticos','postres','Perfectos para fiestas y celebraciones infantiles.',5500.00,'cupcakes2.jpg',40.00,1,0.00,0.00),(606,'Galletas de Sabores','postres','Con sus diferentes rellenos y diferentes sabores.',3800.00,'cookies 2.jpg',40.00,1,0.00,0.00),(607,'Detalle Personalizado','detalles','Incluye postres y decoraciones hechas a medida.',60000.00,'detallepersonalizadp.jpg',40.00,1,0.00,0.00),(608,'Fresas con Chocolate','detalles','Cubiertas con chocolate y decoradas con amor.',40000.00,'fresas.jpg',40.00,1,0.00,0.00),(609,'Fresas Decoradas','detalles','Diseños especiales para regalar o sorprender.',42000.00,'fresas2.jpg',40.00,1,0.00,0.00),(610,'Detalle Día de la Madre','detalles','Ideal para celebrar con algo dulce y elegante.',65000.00,'diadelamadre.jpg',40.00,1,0.00,0.00),(611,'Brownies One Piece','detalles','Brownies decorados con temática de anime.',45000.00,'brownies one piece.jpg',40.00,1,0.00,0.00),(612,'Brownies Temáticos','detalles','Diseños personalizados para cada personaje favorito.',46000.00,'brownies one piece2.jpg',40.00,1,0.00,0.00),(613,'Torta 3 leches','tortas','Torta 3 leches mojadita',50000.00,'torta_3_leches.jpg',40.00,1,0.00,0.00),(614,'Torta de Chocolate','tortas','Chocolatosa y deliciosa',60000.00,'torta_de_chocolate_esponjosa.jpg',40.00,1,0.00,0.00),(615,'Trufas de chocolate','postres','Deliciosas trufas',25000.00,'trufas_de_chocolate.jpg',40.00,1,0.00,0.00);
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recetas`
--

DROP TABLE IF EXISTS `recetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas` (
  `id_receta` int NOT NULL AUTO_INCREMENT,
  `id_producto` int NOT NULL,
  `id_ingrediente` int NOT NULL,
  `cantidad_necesaria` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id_receta`),
  KEY `id_producto` (`id_producto`),
  KEY `id_ingrediente` (`id_ingrediente`),
  CONSTRAINT `recetas_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `recetas_ibfk_2` FOREIGN KEY (`id_ingrediente`) REFERENCES `ingredientes` (`id_ingrediente`)
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas`
--

LOCK TABLES `recetas` WRITE;
/*!40000 ALTER TABLE `recetas` DISABLE KEYS */;
INSERT INTO `recetas` VALUES (61,595,48,50.00),(62,595,51,70.00),(63,595,53,20.00),(64,595,54,150.00),(65,596,46,100.00),(66,596,48,100.00),(67,596,63,2.00),(68,596,51,100.00),(69,596,64,8.00),(70,596,59,200.00),(71,596,89,250.00);
/*!40000 ALTER TABLE `recetas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recetas_empaques`
--

DROP TABLE IF EXISTS `recetas_empaques`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas_empaques` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_producto` int NOT NULL,
  `id_empaque` int NOT NULL,
  `cantidad` int NOT NULL DEFAULT '1',
  `subtotal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_re_producto` (`id_producto`),
  KEY `fk_re_empaque` (`id_empaque`),
  CONSTRAINT `fk_re_empaque` FOREIGN KEY (`id_empaque`) REFERENCES `empaques` (`id_empaque`) ON DELETE CASCADE,
  CONSTRAINT `fk_re_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas_empaques`
--

LOCK TABLES `recetas_empaques` WRITE;
/*!40000 ALTER TABLE `recetas_empaques` DISABLE KEYS */;
INSERT INTO `recetas_empaques` VALUES (2,595,13,1,10000.00),(3,595,30,1,400.00),(4,595,1,1,111.00),(5,595,32,1,12000.00),(6,596,10,1,1500.00),(7,596,30,1,400.00),(8,596,15,1,111.00);
/*!40000 ALTER TABLE `recetas_empaques` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resenas`
--

DROP TABLE IF EXISTS `resenas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resenas` (
  `id_resena` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `calificacion` int DEFAULT NULL,
  `comentario` text,
  `fecha` datetime DEFAULT NULL,
  PRIMARY KEY (`id_resena`),
  KEY `usuario_id` (`usuario_id`),
  KEY `producto_id` (`producto_id`),
  CONSTRAINT `resenas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `resenas_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resenas`
--

LOCK TABLES `resenas` WRITE;
/*!40000 ALTER TABLE `resenas` DISABLE KEYS */;
/*!40000 ALTER TABLE `resenas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `telefono` varchar(50) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `rol` enum('cliente','empleado','admin') DEFAULT 'cliente',
  `fecha_registro` datetime DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (16,'Admin','admin@sweetland.com','pbkdf2:sha256:600000$ddiJe5H8QTXaJ28o$3fb6d9d41639f050d58b46d5b26d8b2d63a0e5acb981dac791636f2cb3d88021',NULL,NULL,'admin',NULL),(18,'Cliente Prueba','cliente@sweetland.com','pbkdf2:sha256:600000$ddiJe5H8QTXaJ28o$3fb6d9d41639f050d58b46d5b26d8b2d63a0e5acb981dac791636f2cb3d88021','3009876543','Avenida 67 #89-10','cliente',NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-02 16:06:08
