<?php
	ini_set('display_errors', 1);
	ini_set('display_startup_errors', 1);
	error_reporting(E_ALL);

	$servername = "localhost";
	$username = "root";
	$password = "root";
	$db = "ekatte";

	$conn = new mysqli($servername, $username, $password, $db);
	$conn->set_charset("utf8");

	if (isset($_POST["city"])){
		$query_param = $_POST["city"];
		$sql = "select naseleni_mesta.name, naseleni_mesta.front, oblast.name, obstini.name, documents.institution, documents.name, region.name, big_region.name from naseleni_mesta INNER JOIN obstini ON naseleni_mesta.fk_obshtini=obstini.Alphabetical_code INNER JOIN oblast ON obstini.oblast_fk=oblast.Alphabetical_code INNER JOIN region ON oblast.region_fk=region.Alphabetical_code	INNER JOIN big_region ON region.big_alpha_code=big_region.Alphabetical_code INNER JOIN documents ON naseleni_mesta.fk_document=documents.id WHERE naseleni_mesta.name LIKE ";
		$sql .= "'";
		$sql .= $query_param;
		$sql .= "%';";

		$data = [];
		$i = 0;
		if ($result = $conn->query($sql)) {
			if($result->num_rows === 0){
				echo "Няма резултати!";
			} else {
				while ($row = $result->fetch_array()) {
					$data[$i] = $row;
					$i += 1;
				}

			}
			$result->close();
		}

		echo json_encode($data);

		$conn->close();
	}

?>
