REATE TABLE IF NOT EXISTS `graph` (
  `name` varchar(100) NOT NULL,
  `template` varchar(2500) NOT NULL,
  `vlabel` varchar(2500) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;





CREATE TABLE IF NOT EXISTS `graphgroups` (
  `graphname` varchar(100) NOT NULL,
  `idgraphgroup` int(10) unsigned NOT NULL,
  `parent` int(10) unsigned NOT NULL,
  PRIMARY KEY (`graphname`,`idgraphgroup`),
  FOREIGN KEY (graphname) REFERENCES graph(name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;






CREATE TABLE IF NOT EXISTS `host` (
  `name` varchar(255) NOT NULL,
  `checkhostcmd` varchar(255) NOT NULL,
  `community` varchar(255) NOT NULL,
  `fqhn` varchar(255) NOT NULL,
  `hosttpl` varchar(255) NOT NULL,
  `mainip` varchar(255) NOT NULL,
  `port` int(10) unsigned NOT NULL,
  `snmpoidsperpdu` int(10) unsigned DEFAULT NULL,
  `snmpversion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;





CREATE TABLE IF NOT EXISTS `service` (
  `name` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `command` varchar(255) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;





CREATE TABLE IF NOT EXISTS `events` (
  `idevent` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `hostname` varchar(100) NOT NULL,
  `servicename` varchar(100) DEFAULT NULL,
  `service_source` varchar(100) NOT NULL,
  `severity` int(10) unsigned NOT NULL,
  `status` enum( 'None', 'Acknowledged', 'Closed' ) NOT NULL DEFAULT 'None',
  `active` bool DEFAULT TRUE,
  `timestamp` datetime DEFAULT NULL,
  `output` text NOT NULL,
  `event_timestamp` datetime DEFAULT NULL,
  `last_check` datetime DEFAULT NULL,
  `recover_output` text,
  `timestamp_active` datetime DEFAULT NULL,
  `timestamp_cleared` datetime DEFAULT NULL,
  `trouble_ticket` varchar(20) DEFAULT NULL,
  `occurence` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`idevent`),
  FOREIGN KEY (`servicename`) REFERENCES service(name),
  FOREIGN KEY (`hostname`) REFERENCES host(name),
  INDEX (`hostname`,`servicename`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;




CREATE TABLE IF NOT EXISTS `event_history` (
  `idhistory` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `type_action` varchar(50) NOT NULL,
  `idevent` int(10) unsigned NOT NULL,
  `key` varchar(255) DEFAULT NULL,
  `value` text,
  `timestamp` datetime DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`idhistory`),
  INDEX (`idevent`),
  FOREIGN KEY ( idevent) REFERENCES events(idevent)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;






CREATE TABLE IF NOT EXISTS `groups` (
  `name` varchar(100) NOT NULL,
  `parent` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`name`),
  FOREIGN KEY (parent) REFERENCES groups(name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE TABLE IF NOT EXISTS `grouppermissions` (
  `groupname` varchar(100) NOT NULL,
  `idpermission` int(10) unsigned NOT NULL,
  FOREIGN KEY (groupname) REFERENCES groups(name),
   PRIMARY KEY (groupname,idpermission)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;






CREATE TABLE IF NOT EXISTS `hostgroups` (
  `hostname` varchar(100) NOT NULL,
  `groupname` varchar(100) NOT NULL,
  PRIMARY KEY (`hostname`,`groupname`),
  FOREIGN KEY (hostname) REFERENCES host(name),
  FOREIGN KEY (groupname) REFERENCES groups(name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;





CREATE TABLE IF NOT EXISTS `servicegroups` (
  `servicename` varchar(100) NOT NULL,
  `groupname` varchar(100) NOT NULL,
  PRIMARY KEY (`servicename`,`groupname`),
  FOREIGN KEY (servicename) REFERENCES service(name),
  FOREIGN KEY (groupname) REFERENCES groups(name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;







CREATE TABLE IF NOT EXISTS `perfdatasource` (
  `hostname` varchar(100) NOT NULL,
  `servicename` varchar(100) NOT NULL,
  `graphname` varchar(100) NOT NULL,
  `type` varchar(100) NOT NULL,
  `label` varchar(255) DEFAULT NULL,
  `factor` float NOT NULL,
  PRIMARY KEY (`hostname`,`servicename`),
  FOREIGN KEY (hostname) REFERENCES host(name),
  FOREIGN KEY (servicename) REFERENCES service(name),
  FOREIGN KEY (graphname) REFERENCES graph(name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




CREATE TABLE IF NOT EXISTS `servicehautniveau` (
  `servicename` varchar(100) NOT NULL,
  `servicename_dep` varchar(100) NOT NULL,
  PRIMARY KEY (`servicename`,`servicename_dep`),
  FOREIGN KEY (servicename) REFERENCES service(name),
  FOREIGN KEY (servicename_dep) REFERENCES service(name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;






CREATE TABLE IF NOT EXISTS `servicetopo` (
  `servicename` varchar(100) NOT NULL,
  `function` varchar(50) NOT NULL,
  PRIMARY KEY (`servicename`),
  FOREIGN KEY (servicename) REFERENCES servicehautniveau(servicename)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

